<template>
    <div v-if="options.report">
        <h4>{{ options.report.title }}</h4>

        <!-- Настройки -->
        <filter-panel :page="options.report.filter_type" :categories="options.report.filters" :patient="patient"
                      :disable_downloading="flags.no_data" :last_date="last_date"
                      :options="options.report.options"/>
        <loading v-if="!flags.loaded"/>
        <nothing-found v-if="flags.no_data"/>

        <!-- Ошибки -->
        <error-block :errors="errors" v-if="errors.length"/>

        <!-- Список страниц -->
        <pagination :selected_page="options.selected_page + 1" :page_cnt="options.page_count"
                    v-if="flags.loaded && !flags.no_data && options.page_count > 1"/>

        <!-- Таблица -->
        <records-table/>

        <!-- Список страниц -->
        <pagination :selected_page="options.selected_page + 1" :page_cnt="options.page_count"
                    v-if="flags.loaded && !flags.no_data && options.page_count > 1"/>


        <!-- Для экспорта -->
        <div v-show="false">
            <report-export :data="records.all" :dates="options.dates" :patient="patient"/>
        </div>

    </div>
</template>

<script>
import RecordsList from "./parts/RecordsList.vue";
import FilterPanel from "../../common/FilterPanel.vue";
import html2pdf from "html2pdf.js";
import Loading from "../../common/Loading.vue";
import ErrorBlock from "../../common/ErrorBlock.vue";
import RecordsTable from "./parts/RecordsTable.vue";
import NothingFound from "../../common/NothingFound.vue";
import Pagination from "./parts/Pagination.vue";
import ReportExport from "./ReportExport.vue";

export default {
    name: "Report",
    components: {ReportExport, Pagination, NothingFound, RecordsTable, Loading, FilterPanel, ErrorBlock, RecordsList},
    props: {
        patient: {
            required: true
        },
        last_date: {
            required: true
        }
    },
    data() {
        return {
            flags: {
                loaded: false,
                no_data: false,
            },
            options: {
                dates: undefined,
                report: {filter_type: ''},
                selected_page: 0,
                page_count: undefined,
                selected_categories: [],
            },
            records: {
                all: undefined
            },
            errors: []
        }
    },
    computed: {
        categories() {
            if (!this.options.report) return []

            return this.options.report.categories
        },
        pages() {
            let start = Math.max(1, this.options.selected_page - 9)
            return this.range_arr(Math.min(20, this.options.page_count),
                this.options.page_count > 20 ? Math.min(start, this.options.page_count - 19) : 1)
        }
    },
    methods: {
        reset_view: function () {
            this.flags.loaded = false
            this.flags.no_data = false
            this.flags.exporting = false

            this.errors = []
        },

        // Данные
        load: function (first_load = false, get_pages_count = false) {
            this.reset_view()
            let categories = this.options.selected_categories.length ? this.options.selected_categories.map(c => c.name) : this.categories

            let dates = this.options.dates.map(date => date ? Math.round(date.getTime() / 1000) : date)
            let options = {
                type: 'report',
                page: this.options.selected_page,
                get_pages_count: get_pages_count,
                first_load: first_load
            }
            this.load_data(categories, dates, options)
        },
        process_load_answer: function () {
            Event.fire('set-dates', this.options.dates)
            Event.fire('refresh-records-table', this.records.all)
            this.flags.loaded = true
        },

        select_page: function (p) {
            if (this.options.selected_page == p) return
            this.options.selected_page = p
            this.load()
        }
    },
    mounted() {
        this.options.selected_page = 0
        this.options.dates = [
            this.start_of_day(this.add_days(this.last_date, -6)),
            this.last_date
        ]
    },
    created() {
        console.log('report-view created')

        // Страница с отчетом открыта
        Event.listen('load-report', (report) => {
            this.options.report = report

            this.options.selected_page = 0
            this.options.selected_categories = []

            // Даты, если установлены в ссылке
            if (window.PARAMS && window.PARAMS.date_from && window.PARAMS.date_to) {
                this.options.dates = [
                    new Date(window.PARAMS.date_from),
                    new Date(window.PARAMS.date_to)
                ]
            } else {
                // Даты по умолчанию
                this.options.dates = [
                    undefined,
                    this.last_date
                ]
            }

            // Обновление дат в строке фильтров
            Event.fire('set-dates', this.options.dates)

            this.load(!window.PARAMS.mode, true)
            this.$forceUpdate()
        })

        // Записи получены
        Event.listen('report-data-loaded', (data) => {
            this.reset_view()

            // Обновление дат
            if (data.info.first_load) {
                this.options.dates = [
                    new Date(data.info.dates[0] * 1000),
                    new Date(data.info.dates[1] * 1000)
                ]
            }

            // Сохранение записей
            this.records.all = data.records.sort((a, b) => {
                return a.timestamp > b.timestamp ? -1 : a.timestamp < b.timestamp ? 1 : 0
            })

            this.flags.no_data = !data.records.length

            if (data.info.page_count)
                this.options.page_count = data.info.page_count

            this.process_load_answer()
        })

        // Обновление дат
        Event.listen('report-update-dates', (dates) => {
            this.options.selected_page = 0
            this.options.dates = dates
            this.load(false, true)
        })

        // Неверные даты
        Event.listen('incorrect-dates', (duration) => {
            this.errors = this.add_error(this.error_messages.incorrect_period)
        })

        // Обновление категорий
        Event.listen('update-categories', (categories) => {
            this.options.selected_page = 0
            this.options.selected_categories = categories
            this.load(false, true)
        })

        // Страница
        Event.listen('select-page', (p) => this.select_page(p - 1))
    },
}
</script>

<style>
.to-export {
    font-size: smaller;
}
</style>