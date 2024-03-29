<template>
    <div>
        <loading v-if="!flags.ready"/>
        <highcharts constructor-type="stockChart" class="highcharts"
                    :options="to_export ? export_options : highcharts_options" v-else/>
    </div>
</template>

<script>
import {Chart} from 'highcharts-vue'
import Highcharts from "highcharts";
import stockInit from 'highcharts/modules/stock'
import boost from "highcharts/modules/boost";
import 'highcharts/modules/heatmap.src.js';
import heatmap from "highcharts/modules/heatmap";
import Loading from "../../../common/Loading.vue";

stockInit(Highcharts)
boost(Highcharts)
heatmap(Highcharts);

export default {
    name: "Heatmap",
    components: {Loading, highcharts: Chart},
    props: {
        data: {required: true},
        graph: {required: true},
        to_export: {required: false}
    },
    data() {
        return {
            flags: {
                ready: false,
                show_optional: false
            },
            highcharts_options: {},
            export_options: {},
            options: {
                colors: [],
                dates: []
            },
            series: {
                required: [],
                optional: []
            },
            records: {
                all: undefined,
                by_categories: undefined,
            }
        }
    },
    computed: {},
    methods: {
        reset_view: function () {
            this.flags.ready = false

            this.series = {
                required: undefined,
                optional: undefined
            }
        },
        update_heatmap: function () {
            if (!this.highcharts_options) return

            this.flags.ready = false
            this.highcharts_options.series = this.get_series()

            this.delay(0).then(() => {
                if (this.highcharts_options.series) {
                    this.set_axis_height()

                    if (this.to_export) {
                        this.set_export_options()
                    }

                    console.log("should be ready!")

                    this.flags.ready = true
                    this.$forceUpdate()
                }
            });
        },

        // График
        set_export_options: function () {
            this.export_options = JSON.parse(JSON.stringify(this.highcharts_options))

            this.export_options.chart.width = 700
            this.export_options.chart.height -= 3
            this.export_options.chart.backgroundColor = this.colors.background[1]
            this.export_options.xAxis.labels.style = {fontSize: '10px'}
            this.export_options.yAxis[0].labels.style = {fontSize: '10px'}
        },
        set_heatmap_options: function () {
            // chart
            this.highcharts_options.chart.type = 'heatmap'
            this.highcharts_options.chart.marginLeft = undefined
            this.highcharts_options.chart.zoomType = ''

            this.highcharts_options.navigator = {enabled: false}

            // x axis
            this.highcharts_options.xAxis.gridLineWidth = 0
            this.highcharts_options.xAxis.minorGridLineWidth = 0
            this.highcharts_options.xAxis.max = +this.options.dates[1] - this.day


            // y axis 0
            this.highcharts_options.yAxis[0].reversed = true
            this.highcharts_options.yAxis[0].gridLineWidth = 0
            this.highcharts_options.yAxis[0].offset = 0
            this.highcharts_options.yAxis[0].labels = {
                enabled: true,
                align: 'left',
                x: 5,
                y: 4
            }

            // y axis 1
            this.highcharts_options.yAxis.splice(1, 1)

            // colors
            this.highcharts_options.colorAxis = {
                stops: [
                    [0, this.colors.green[0]], [0.1, this.colors.yellow[0]], [1, this.colors.red[0]]
                ],
                min: 0,
                max: 1
            }

            if (this.graph.options.regular_scale) {
                this.highcharts_options.colorAxis.stops = this.colors.scale.map((color, index) => [index / 10, color])
            }

            // tooltip
            this.highcharts_options.tooltip.pointFormatter = undefined
            this.highcharts_options.tooltip.positioner = undefined

            // legend
            this.highcharts_options.legend = {enabled: false}

            this.update_heatmap()
        },
        set_axis_height: function () {
            if (!this.highcharts_options) return
            let count = 0

            if (this.series.required) count += this.series.required.length
            if (this.series.optional && this.flags.show_optional) count += this.series.optional.length

            this.highcharts_options.yAxis[0].categories = this.series.required.map((s) => s.name)
            if (this.series.optional && this.flags.show_optional)
                this.highcharts_options.yAxis[0].categories = this.highcharts_options.yAxis[0].categories
                    .concat(this.series.optional.map((s) => s.name))

            this.highcharts_options.yAxis[0].height = 25 * count

            this.highcharts_options.chart.height = count * 25 + 63
        },

        // Записи
        get_records_by_category_by_key: function (category, param_key = 'symptom_group', max_value = 10, text_category = false) {
            let records_by_param = {}

            this.records.by_categories[category].forEach((record) => {
                let x = +this.start_of_day(new Date((record.timestamp) * 1000))

                let record_params = record.params ? record.params : {}
                let group = record_params[param_key] ?
                    (record_params[param_key]) :
                    (text_category ? record.value : record.category_info.description)

                let color = text_category ? (record_params.color) : (record.value / max_value)
                if (color == undefined) color = 0.7

                let value = record.value

                if (record.category_code == 'medicine') {
                    color = -1
                    value = record_params.dose == null ? 'Доза не указана' : `Доза: ${record.params.dose}`
                }

                let point = {
                    description: value,
                    timestamp: record.timestamp,
                    formatted_date: record.formatted_date,
                    formatted_time: record.formatted_time,
                }

                let data = {
                    points: [point],
                    description: `<b>${record.category_info.description}: ${group}</b>`,
                    formatted_date: record.formatted_date,
                    color: color,
                    x: x
                }

                if (group in records_by_param) {
                    let old = records_by_param[group].find(s => s.x == data.x)
                    if (old) {
                        old.color = old.color > color ? old.color : color
                        old.points.push(point)
                    } else {
                        records_by_param[group].push(data)
                    }
                } else {
                    records_by_param[group] = [data]
                }
            })

            return records_by_param
        },

        // Точки
        get_series: function () {
            let check_series = (type, y_offset = 0) => {
                let s = this.series[type]
                if (!s) {
                    s = this.get_category_series(this.graph[type + '_categories'], y_offset)
                    this.series[type] = s
                }
                return s
            }

            let series = check_series('required')

            let optional = []

            if (this.flags.show_optional)
                optional = check_series('optional', series.length)

            series = series.concat(optional)
            series = series.filter((s) => s != undefined)

            return series
        },
        get_category_series: function (categories, y_offset = 0) {
            let series = []
            if (!categories) return series

            let y = y_offset
            categories.forEach((category) => {
                let records = this.records.by_categories[category]
                if (!records) return undefined

                let is_text_category = records[0].category_type == 'string'


                let param = this.graph.options.group_params ? this.graph.options.group_params[category] : 'symptom_group'
                let max_value = this.graph.options.max_values ? this.graph.options.max_values[category] : 10
                let records_by_param = this.get_records_by_category_by_key(category, param, max_value, is_text_category)

                let tmp = Object.entries(records_by_param).map(([rec, rec_data]) => {
                    rec_data.forEach(data => {
                        data.points.sort((a, b) => a.timestamp - b.timestamp)
                        data.points.forEach(p => {
                            data.description += `<br>• <b>${p.formatted_time}</b> - ${p.description}`
                        })
                    })

                    let series_data = {
                        description: rec,
                        name: category,
                        records: rec_data,
                        y: y
                    }

                    y += 1
                    return this.prepare_series(series_data)
                });

                series = series.concat(tmp)
            })

            return series
        },
        prepare_series: function (data) {
            let series = {
                name: data.description,
                category_code: data.name,
                category_type: data.category_type,
                data: this.prepare_values(data),
                showInNavigator: false,
                states: {
                    inactive: {opacity: 1}
                },
                dataGrouping: {enabled: false},
                yAxis: 0,
                colsize: this.day,
                connectNulls: true,
                nullColor: this.color_transparency(this.colors.green[0], 50),
                borderWidth: 2,
                borderColor: this.colors.background[+this.to_export]
            }

            if (data.name == 'medicine') {
                series.nullColor = this.color_transparency(this.colors.medsenger[2], 40)
            }

            return series
        },
        prepare_values: function (data) {
            let res

            let get_point_template = (rec) => {
                return {
                    dataLabels: {
                        enabled: true,
                        format: '{point.cnt}',
                        filter: {
                            operator: '>',
                            value: 1,
                            property: 'cnt'
                        }
                    },
                    x: rec.x,
                    y: data.y,
                    value: rec.color,
                    cnt: rec.points.length,
                    name: data.name,
                    formatted_date: rec.formatted_date,
                    comment: this.get_comment(rec, data.description)
                }
            }

            res = data.records.map((rec) => {
                return get_point_template(rec)
            })
            if (data.name == 'medicine') {
                res = res.map((rec) => {
                    rec.dataLabels.filter = undefined
                    rec.color = this.colors.medsenger[2]
                    return rec
                })
            }
            res = this.fill_nulls(res, data.y)

            return res
        },

        // Вспомогательные
        get_comment: function (point, category) {
            return `<u>${point.formatted_date}</u><br>${point.description}`
        },
        fill_nulls: function (data, y) {
            let start = +this.start_of_day(new Date(this.options.dates[0].getTime()))
            let end = +this.start_of_day(new Date(this.options.dates[1].getTime()))


            let i = 0
            let res = []

            while (end >= start) {
                if (i >= data.length || end != data[i].x) {
                    res.push({
                        dataLabels: {enabled: false},
                        x: end,
                        y: y,
                        value: null,
                        comment: `Нет данных`,
                    })
                } else {
                    res.push(data[i])
                    i += 1
                }
                end -= this.day
            }
            return res
        },
    },
    mounted() {
        Highcharts.setOptions({
            lang: {
                months: this.descriptions.months,
                weekdays: this.descriptions.weekdays,
                shortMonths: this.descriptions.shortMonths
            }
        });

        // Первая отрисовка графика
        Event.listen('draw-graph', (options) => {
            if (!this.constants.heatmap_types.includes(this.graph.type)) return
            this.reset_view()

            this.records.all = this.data.all
            this.records.by_categories = this.data.by_categories
            this.records.optional = undefined

            this.copy(this.highcharts_options, options)
            this.set_heatmap_options()
        })

        // Режимы отображения
        Event.listen('update-legend', (mode) => {
            this.flags.show_legend = mode
            this.update_graph()
        });

        Event.listen('update-optional', (mode) => {
            this.flags.show_optional = mode
            this.update_heatmap()
        });


        // Размер окна
        Event.listen('window-resized', () => {
            if (this.options.highcharts_options) this.$forceUpdate()
        });


        // Обновление дат
        Event.listen('set-dates', (dates) => {
            this.options.dates = [
                dates[0] ? this.start_of_day(dates[0]) : undefined,
                dates[1] ? this.end_of_day(dates[1]) : undefined
            ]

            this.$forceUpdate()
        });
    }
}
</script>

<style scoped>
.highcharts {
    overflow: visible !important;
    margin-left: -10px;
}
</style>