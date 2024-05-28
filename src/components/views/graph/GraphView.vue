<template>
    <div v-show="options.graph">
        <h4>{{ options.graph.title }}</h4>

        <!-- Настройки -->
        <filter-panel :page="options.graph.filter_type" :patient="patient"
                      :disable_downloading="flags.no_data"
                      :options="options.graph.options"/>


        <!-- График -->
        <loading v-if="!flags.loaded"/>
        <nothing-found v-if="flags.no_data"/>
        <small class="text-muted" v-show="mobile && flags.loaded && !flags.no_data">* Поверните экран, чтобы расширить
            график</small>

        <line-graph :data='records' :dates="options.dates" :graph="options.graph" :to_export="false"
                    v-show="options.graph.type == 'line-graph' && flags.loaded && !flags.no_data"/>
        <day-line-graph :data='records' :dates="options.dates" :graph="options.graph" :to_export="false"
                        v-show="options.graph.type == 'day-graph' && flags.loaded && !flags.no_data"/>

        <div v-for="(current_heatmap, i) in heatmaps" v-show="options.graph.type == 'heatmap' && heatmaps.length > 0">
            <h6 v-if="heatmaps.length > 1">{{ current_heatmap.title }}</h6>

            <heatmap :subtitle="current_heatmap.title" :data='current_heatmap.records' :dates="options.dates" :graph="options.graph"
                     :to_export="false"
                     v-show="flags.loaded && !flags.no_data"/>
        </div>


        <!-- Ошибки -->
        <error-block :errors="errors"/>

        <!-- Статистика -->
        <stats-table :data="records" :graph="options.graph"
                     v-show="['line-graph', 'day-graph'].includes(options.graph.type) && flags.loaded && !flags.no_data"/>

        <!-- Табличка с симптомами -->
        <div class="center" v-if="list_data.length">
            <h5 class="text-center">Симптомы и события</h5>
            <records-table :data="list_data"/>
        </div>

        <!-- Для экспорта -->
        <div v-show="false">
            <graph-export :data='records' :dates="options.dates" :patient="patient"/>
        </div>

    </div>
</template>

<script>

import FilterPanel from "../../common/FilterPanel.vue";
import ErrorBlock from "../../common/ErrorBlock.vue";
import Loading from "../../common/Loading.vue";
import LineGraph from "./graph-types/LineGraph.vue";
import NothingFound from "../../common/NothingFound.vue";
import StatsTable from "./parts/StatsTable.vue";
import Heatmap from "./graph-types/Heatmap.vue";
import GraphExport from "./GraphExport.vue";
import DayLineGraph from "./graph-types/DayLineGraph.vue";
import RecordsTable from "../report/parts/RecordsTable.vue";


export default {
    name: "GraphView",
    components: {
        RecordsTable,
        DayLineGraph,
        GraphExport,
        Heatmap,
        StatsTable,
        NothingFound,
        LineGraph,
        Loading,
        ErrorBlock,
        FilterPanel
    },
    props: {
        patient: {required: true},
        last_date: {required: true}
    },
    data() {
        return {
            errors: [],
            flags: {
                no_data: false,
                loaded: false
            },
            options: {
                dates: undefined,
                graph: {filter_type: ''},
                text_categories: ['symptom', 'medicine', 'patient_comment', 'information', 'side_effect'],
                highcharts_options: undefined
            },
            records: {
                all: undefined,
                by_categories: undefined
            },
            heatmaps: []
        }
    },
    computed: {
        days_count() {
            return Math.ceil((this.options.dates[1] - this.options.dates[0]) / this.day)
        },
        by_hours() {
            return this.days_count < 4
        },
        list_data() {
            if (this.flags.no_data || !this.records.all) return []

            return this.records.all.filter(record =>
                this.options.text_categories.includes(record.category_info.name))
        },
        width() {
            return this.mobile ? (window.innerWidth + 10) : (window.innerWidth * 0.9)
        }
    },
    methods: {
        reset_view: function () {
            this.flags.loaded = false
            this.flags.no_data = false

            this.errors = []
        },

        // Данные
        load: function (first_load) {
            this.reset_view()
            let categories = this.options.graph.categories
            let required_categories = this.options.graph.required_categories

            let dates = this.options.dates.map(date => date ? Math.round(date.getTime() / 1000) : date)
            let options = {
                type: this.options.graph.type,
                first_load: first_load,
            }

            this.load_data(categories, dates, options, required_categories)
        },
        process_load_answer: function () {
            Event.fire('set-dates', this.options.dates)
            this.options.highcharts_options = this.get_highcharts_options()

            this.flags.loaded = true
            if (!this.flags.no_data) {
                Event.fire('draw-graph', this.get_highcharts_options)
                Event.fire('refresh-records-table', this.list_data)
            }
        },

        // Графики
        get_highcharts_options: function () {
            return {
                chart: {
                    boostThreshold: 500,
                    turboThreshold: 0,
                    animation: false,
                    zoomType: this.mobile ? '' : 'x',
                    backgroundColor: this.colors.background[0],
                    marginLeft: 30,
                    height: `${window.innerHeight - 230}`,
                    width: this.width,
                    events: {}
                },
                accessibility: {enabled: false},
                series: [],
                time: {useUTC: false},
                xAxis: {
                    type: 'datetime',
                    offset: 0,
                    gridLineWidth: 1,
                    minorGridLineWidth: 2,
                    minorTickLength: 0,
                    tickInterval: this.by_hours ? (60 * 60 * 1000) : this.day,
                    minorTickInterval: this.by_hours ? (60 * 60 * 1000) : this.day,
                    min: +this.options.dates[0],
                    max: +this.options.dates[1] + (this.by_hours ? (10 * 60 * 1000) : 0),
                    ordinal: false,
                    dateTimeLabelFormats: {
                        day: '%d.%m',
                        hour: '%H:%M'
                    },
                    labels: {rotation: -45}
                },
                yAxis: [
                    this.get_y_axis(0),
                    this.get_y_axis(1)
                ],
                tooltip: {
                    borderWidth: 2,
                    useHTML: true,
                    formatter: function () {
                        let point = this.point ? this.point : this.points[0];
                        return point.comment
                    },
                    pointFormatter: function () {
                        let point = this;
                        return point.series.userOptions.data.filter(p => p.x == point.x).map(p => {
                            return p.comment
                        }).join('<br>')
                    },
                    positioner: function () {
                        return {x: 30, y: 10};
                    },
                    shadow: false,
                    backgroundColor: 'rgba(255,255,255,0.8)',
                    shared: true,
                    headerFormat: null
                },
                legend: {width: '100%'},
                plotOptions: {},
                rangeSelector: {enabled: false},
                navigator: {enabled: false},
                scrollbar: {enabled: false}
            }
        },
        get_y_axis: function (index) {
            return {
                title: {},
                gridLineWidth: 1,
                lineWidth: 2,
                offset: index ? 0 : undefined,
                resize: {enabled: true},
            }
        }
    },
    mounted() {
        this.options.dates = [
            this.start_of_day(this.add_days(this.last_date, -13)),
            this.last_date
        ]
    },
    created() {
        console.log('graph-view created')

        // Страница с графиком открыта
        Event.listen('load-graph-view', (params) => {
            this.options.graph = params

            // Даты, если установлены в ссылке
            if (window.PARAMS && window.PARAMS.date_from && window.PARAMS.date_to) {
                this.options.dates = [
                    new Date(window.PARAMS.date_from),
                    new Date(window.PARAMS.date_to)
                ]
            } else {
                // Даты по умолчанию
                this.options.dates = [
                    this.start_of_day(this.add_days(this.last_date, -13)),
                    this.last_date
                ]
            }

            // Обновление дат в строке фильтров
            Event.fire('set-dates', this.options.dates)

            // Запрос записей у сервера
            this.load(!window.PARAMS.mode)
            this.$forceUpdate()
        })

        // Записи получены
        Event.listen('graph-data-loaded', (data) => {
            this.reset_view()

            // Обновление дат
            if (data.info.first_load) {
                this.options.dates = [
                    new Date(data.info.dates[0] * 1000),
                    new Date(data.info.dates[1] * 1000)
                ]
            }

            if (!this.options.dates[0]) {
                this.options.dates[0] = new Date(data.records[data.records.length - 1].timestamp * 1000)
            }

            // Сохранение записей
            this.records.all = data.records.sort((a, b) => {
                return a.timestamp > b.timestamp ? -1 : a.timestamp < b.timestamp ? 1 : 0
            })
            this.records.by_categories = this.group_by(this.records.all, 'category_code')

            if (this.options.graph.type === 'heatmap') {
                this.heatmaps = []
                let subcategories = {}
                const subcategory_extractor = (record) => {
                    if (!record.params.subcategory) {
                        record.params.subcategory = 'Общее'
                    }
                    if (!subcategories[record.params.subcategory]) {
                        subcategories[record.params.subcategory] = [record]
                    } else {
                        subcategories[record.params.subcategory].push(record)
                    }
                }

                this.records.all.map(subcategory_extractor)

                Object.keys(subcategories).forEach((subcategory_title) => {
                    this.heatmaps.push({
                        title: subcategory_title,
                        records: {
                            all: subcategories[subcategory_title],
                            by_categories: this.group_by(subcategories[subcategory_title], 'category_code')
                        }
                    })
                })
            }

            this.flags.no_data = this.options.graph.required_categories.every((c) => !this.records.by_categories[c])

            this.delay(0).then(this.process_load_answer)
        })

        // Неверные даты
        Event.listen('incorrect-dates', (duration) => {
            if (duration < 0) this.add_error(this.errors, this.error_messages.incorrect_period)
            else if (duration > 30 && this.errors[0] != this.error_messages.not_more_30_days)
                this.errors.unshift(this.error_messages.not_more_30_days)
        });

        // Обновление дат
        Event.listen('graph-update-dates', (dates) => {
            this.options.dates = dates
            this.load()
        });

        // Размер окна
        Event.listen('window-resized', () => {
            if (this.options.highcharts_options)
                this.options.highcharts_options.chart.width = this.mobile ? (window.innerWidth + 10) : (window.innerWidth * 0.9)

        })

        // Ошибки
        Event.listen('update-graph-view-errors', (errors) => {
            this.errors = errors.map((e) => this.error_messages[e])
        })
    }
}

</script>

<style>
</style>