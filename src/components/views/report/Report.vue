<template>
    <div v-if="options.report">
        <h4>{{ options.report.title }}</h4>
        <filter-panel page="report" :categories="options.report.filters" :patient="patient"
                      :disable_downloading="!records || !records.length" :last_date="last_date"/>
        <loading v-if="!options.loaded"/>
        <div v-else>
            <!-- Ошибки -->
            <error-block :errors="errors" v-if="errors.length"></error-block>
            <!-- Записи -->
            <records-list :data="records"/>

            <!-- Список страниц -->
            <div style="text-align: center" v-if="options.page_count">
                <button class="btn btn-link btn-sm" @click="select_page(0)"
                        v-if="options.selected_page > 9">
                    &#8676;
                </button>
                <button class="btn btn-link btn-sm" @click="select_page(options.selected_page - 1)"
                        v-if="options.selected_page > 0">
                    &#8592;
                </button>
                <a class="btn btn-link btn-sm" @click="select_page(page - 1)" v-for="(page, index) in pages"
                   :style="page == (options.selected_page + 1) ? 'font-weight: bold; text-decoration: underline; color: black;' : ''">{{
                        page
                    }}</a>
                <button class="btn btn-link btn-sm" @click="select_page(options.selected_page + 1)"
                        v-if="options.selected_page < options.page_count - 2">
                    &#8594;
                </button>
                <button class="btn btn-link btn-sm" @click="select_page(options.page_count - 1)"
                        v-if="options.selected_page < options.page_count - 10">
                    &#8677;
                </button>
            </div>

            <!-- Для экспорта -->
            <div v-show="false" v-if="options.loaded && records">
                <div ref="to-export" class="to-export">
                    <h4>{{ options.report.title }}</h4>
                    <br>
                    <h6>Пациент: {{ patient.name }} ({{ patient.birthday }})</h6>
                    <hr>
                    <records-list :data="records" :to_export="true"/>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
import RecordsList from "./parts/RecordsList.vue";
import FilterPanel from "../../common/FilterPanel.vue";
import html2pdf from "html2pdf.js";
import Loading from "../../common/Loading.vue";
import ErrorBlock from "../../common/ErrorBlock.vue";

export default {
    name: "Report",
    components: {Loading, FilterPanel, ErrorBlock, RecordsList},
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
            options: {
                loaded: false,
                report: undefined,
                dates: undefined,
                selected_page: 0,
                page_count: undefined,
                selected_categories: [],
            },
            records: [],
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
        load: function (get_pages_count = false) {
            this.options.loaded = false
            this.errors = []

            let categories = this.options.selected_categories.length ? this.options.selected_categories.map(c => c.name) : this.categories
            let dates = this.options.dates.map(date => date ? date.getTime() / 1000 : date)
            let options = {
                type: 'report',
                page: this.options.selected_page,
                get_pages_count: get_pages_count
            }
            this.load_data(categories, dates, options)
        },
        select_page: function (p) {
            this.options.selected_page = p
            this.load()
        },
        generate_report: function () {
            let element = this.$refs['to-export']

            let opt = {
                margin: 0.5,
                filename: this.patient.name + '.pdf',
                page_break: {mode: 'css'},
                // image:        { type: 'jpeg', quality: 0.98 },
                html2canvas: {dpi: 192, letterRendering: true},
                jsPDF: {unit: 'in', format: 'a4', orientation: 'portrait'}
            };

            html2pdf().set(opt).from(element).save();
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
        Event.listen('loaded', (data) => {
            if (data.info.type != 'report') return
            this.records = data.records
            Event.fire('set-dates', this.options.dates)

            if (data.info.page_count)
                this.options.page_count = data.info.page_count
            this.options.loaded = true
        })
        Event.listen('load-report', (report) => {
            this.options.selected_page = 0
            this.options.report = report

            if (window.PARAMS && window.PARAMS.date_from && window.PARAMS.date_to) {
                this.options.dates = [
                    new Date(window.PARAMS.date_from),
                    new Date(window.PARAMS.date_to)
                ]
            }

            this.load(true)
        })

        Event.listen('report-update-dates', (dates) => {
            this.options.selected_page = 0
            this.options.dates = dates
            this.load(true)
        })

        Event.listen('update-categories', (categories) => {
            this.options.selected_page = 0
            this.options.selected_categories = categories
            this.load(true)
        })

        Event.listen('generate-report', () => {
            if (this.options.loaded)
                this.generate_report()
        })

        Event.listen('incorrect-dates', (duration) => {
            this.errors = this.add_error(this.error_messages.incorrect_period)
        })

        Event.listen('back-to-dashboard', () => {
            this.options.loaded = false;
        });

    },
}
</script>

<style>
.to-export {
    font-size: smaller;
}
</style>