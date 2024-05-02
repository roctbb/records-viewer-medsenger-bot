<template>
    <div>
        <loading v-if="!flags.ready"/>
        <highcharts class="chart" constructor-type="stockChart"
                    :options="to_export ? export_options : highcharts_options" v-else/>
    </div>
</template>

<script>
import {Chart} from 'highcharts-vue'
import Highcharts from "highcharts";
import stockInit from 'highcharts/modules/stock'
import boost from "highcharts/modules/boost";
import arearange from 'highcharts/highcharts-more';
import Loading from "../../../common/Loading.vue";
import * as moment from "moment";


stockInit(Highcharts)
boost(Highcharts)
arearange(Highcharts);


export default {
    name: "DayLineGraph",
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
                show_legend: true,
            },
            highcharts_options: {},
            export_options: {},
            options: {
                colors: [],
                dates: []
            },
            series: {
                clear: undefined,
            },
            records: {
                all: undefined,
                by_categories: undefined,
            }
        }
    },
    computed: {
        too_much_points() {
            return this.records.all &&
                this.records.all.length > 500
        }
    },
    methods: {
        reset_view: function () {
            this.flags.ready = false

            this.series = {
                clear: undefined,
            }
        },
        update_graph: function () {
            if (!this.highcharts_options) return

            this.flags.ready = false
            this.highcharts_options.series = this.get_series()
            this.highcharts_options.legend.enabled = this.flags.show_legend

            this.delay(0).then(() => {
                if (this.highcharts_options.series) {
                    if (this.to_export) {
                        this.set_export_options()
                    }

                    this.flags.ready = true
                    this.$forceUpdate()
                }
            });
        },

        // График
        set_export_options: function () {
            this.export_options = JSON.parse(JSON.stringify(this.highcharts_options))

            this.export_options.chart.events.render = function (event) {
                Event.fire('set-export-chart', this)
            }
            this.export_options.chart.width = 700
            this.export_options.chart.height = 500
            this.export_options.chart.backgroundColor = this.colors.background[1]
            this.export_options.xAxis.labels.style = {fontSize: '10px'}
            this.export_options.yAxis[0].labels.style = {fontSize: '10px'}
            this.export_options.series.forEach(series => {
                series.data.forEach(val => {
                    if (val.marker && val.marker.symbol && val.marker.symbol.includes('url')) {
                        val.marker.symbol = 'circle'
                        val.marker.fillColor = this.colors.red[0]
                    }
                    val.dataLabels.formatter = function () {
                        return `${val.y} (${val.formatted_date})`
                    }
                })
            })

        },
        set_day_line_graph_options: function () {
            // chart
            this.highcharts_options.chart.type = 'line'
            this.highcharts_options.chart.height = `${Math.max(window.innerHeight - 150, 500) + (this.mobile ? 150 : 0)}px`
            this.highcharts_options.chart.events = {
                render: function (event) {
                    let data = {
                        start: event.target.axes[0].min,
                        end: event.target.axes[0].max
                    }
                    Event.fire('refresh-stats', data)
                    Event.fire('set-export-chart-extremes', {
                        start: event.target.axes[0].min,
                        end: event.target.axes[0].max
                    })
                }
            }

            this.highcharts_options.navigator = {
                enabled: true,
                xAxis: {labels: {enabled: false}}
            }

            // x axis
            this.highcharts_options.xAxis.tickInterval = 60 * 60 * 1000
            this.highcharts_options.xAxis.minorTickInterval = 60 * 60 * 1000
            this.highcharts_options.xAxis.dateTimeLabelFormats.day = '00:00'
            let today = new Date()

            today.setHours(5, 0, 0, 0)
            this.highcharts_options.xAxis.min = today.getTime()

            today.setMinutes(30)
            this.highcharts_options.xAxis.max = today.getTime() + this.day

            // y axis 0
            this.highcharts_options.yAxis[0].title = {text: 'Значения в пределах суток'}
            this.highcharts_options.yAxis[0].offset = 5
            this.highcharts_options.yAxis[0].labels = {
                align: 'right',
                x: -5,
                rotation: 0,
                enabled: true
            }
            this.highcharts_options.yAxis[0].height = '100%'

            // y axis 1
            this.highcharts_options.yAxis.splice(1, 1)

            // colors
            this.highcharts_options.colors = this.options.show_points_colors ?
                this.colors.gray : this.options.colors

            // tooltip
            this.highcharts_options.tooltip.formatter = undefined
            if (!this.mobile) {
                this.highcharts_options.tooltip.positioner = undefined
            }

            // plot
            this.highcharts_options.plotOptions = {
                line: {
                    dataLabels: {enabled: true}
                },
                series: {
                    marker: {
                        lineWidth: 1,
                        lineColor: null,
                    }
                }
            }

            // legend
            this.highcharts_options.legend = {
                maxHeight: this.mobile ? 50 : 100,
                enabled: this.flags.show_legend
            }

            this.update_graph()
        },

        // Точки
        get_series: function () {
            let series = this.get_number_series()
            series = series.filter((s) => s != undefined)
            return series
        },
        get_number_series: function () {
            let series = this.series.clear

            let get_clear_series = () => {
                series = []
                Object.entries(this.records.by_categories).forEach(([category, records]) => {
                    if (records[0].category_type != 'string') {
                        let series_data = {
                            name: category,
                            description: records[0].category_info.description,
                            marker: 'circle'
                        }
                        series.push(this.prepare_series(series_data))
                    }
                })

                return series
            }

            if (!series) {
                series = get_clear_series()
                this.series.clear = series
            }

            return series
        },

        prepare_series: function (data) {
            if (!data.records)
                data.records = this.records.by_categories[data.name]

            if (!data.records) return undefined

            data.records = data.records.sort((a, b) => a.timestamp - b.timestamp)
            data.category_type = data.records[0].category_type

            let series = {
                name: data.description,
                category_code: data.name,
                category_type: data.category_type,
                data: this.prepare_values(data),
                showInNavigator: true,
                states: {
                    inactive: {opacity: 1},
                    hover: {enabled: false}
                },
                marker: {
                    enabled: true,
                    radius: 4,
                    symbol: data.marker
                },
                dataGrouping: {enabled: false},
                yAxis: 0,
                lineWidth: 0,
                dashStyle: undefined
            }

            return series
        },
        prepare_values: function (data) {
            let res

            let today = new Date()
            let today_arr = [today.getFullYear(), today.getMonth(), today.getDate()]

            let get_point_template = (rec) => {
                let date = new Date(rec.timestamp * 1000)
                date.setFullYear(today_arr[0], today_arr[1], today_arr[2])
                if (date.getHours() < 5) date = this.add_days(date, 1)
                rec.timestamp = date.getTime() / 1000

                return {
                    dataLabels: {
                        enabled: true,
                        formatter: function () {
                            return `${rec.value} (${rec.formatted_date})`
                        },
                    },
                    x: date.getTime(),
                    y: data.y,
                    timestamp: rec.timestamp,
                    formatted_date: rec.formatted_date,
                    formatted_time: rec.formatted_time,
                    formatted_hours: rec.formatted_hours,
                    comment: this.get_comment(rec, data.description)
                }
            }

            res = data.records.map((rec) => {
                let point = get_point_template(rec)
                point.y = rec.value
                point.value = rec.value
                point.marker = this.get_marker(rec)
                return point
            })

            res = res.sort((a, b) => a.x - b.x)

            return res
        },

        // Вспомогательные
        get_marker: function (point) {
            return {
                symbol: this.get_symbol(point),
                lineColor: this.get_color(point),
                fillColor: this.get_color(point),
                radius: this.get_radius(point)
            }
        },
        get_color: function (point) {
            if (point) {
                if (this.flags.show_colors) {
                    let c = this.get_color_from_additions(point)
                    if (this.colors[c])
                        return this.colors[c][0]
                    return c
                }

                if (this.has_warning(point)) {
                    return this.colors.red[0];
                }
            }

            return undefined;
        },
        has_warning(point) {
            let additions = this.comment_additions(point)
            if (!additions || additions.length === 0) return false

            let show_warning = true

            additions.forEach(addition => {
                if (!this.is_warning_addition(addition)) {
                    show_warning = false
                }
            })

            return show_warning
        },
        get_symbol: function (point) {
            if (this.has_warning(point) && !this.flags.show_points_colors) {
                return 'url(' + this.images.warning + ')'
            }
        },
        get_radius: function (point) {
            return point.additions ? 6 : undefined
        },
        get_comment: function (point, category) {
            let comment = `<u>${point.formatted_date}</u><br><b>${point.formatted_time}</b> - ${category}: ${point.value}`

            this.comment_additions(point).forEach((value) => {
                if (this.is_warning_addition(value)) {
                    comment += `<br><b style="color: red;">${value['addition']['comment']}</b>`
                } else {
                    comment += `<br>${value['addition']['comment']}`
                }
            })

            if (point.comments && point.comments.length) {
                comment += `<br><b>Дополнительная информация:</b>`
                point.comments.forEach((value) => {
                    comment += `<br>${value.value}`
                })
            }

            let zone = this.zone_addition(point)
            if (this.flags.show_colors && zone) {
                let color = this.color_transparency(zone['color'], 30)
                comment += `<br><b style="background-color: ${color};">${zone['zone_description']}</b>`
            }

            return comment
        },
    },
    mounted() {
        this.options.colors = [this.colors.blue[0], this.colors.green[0], this.colors.pink[0], this.colors.purple[0], this.colors.yellow[0],
            this.colors.blue[2], this.colors.green[2], this.colors.pink[2], this.colors.purple[2], this.colors.yellow[2]]

        Highcharts.setOptions({
            lang: {
                months: this.descriptions.months,
                weekdays: this.descriptions.weekdays,
                shortMonths: this.descriptions.shortMonths
            }
        });

        // Первая отрисовка графика
        Event.listen('draw-graph', (options_getter) => {
            if (!this.constants.day_graph_types.includes(this.graph.type)) return
            this.reset_view()

            this.records.all = this.data.all
            this.records.by_categories = this.data.by_categories

            this.highcharts_options = options_getter()
            this.set_day_line_graph_options()
        })

        // Режимы отображения
        Event.listen('update-legend', (mode) => {
            if (!this.constants.day_graph_types.includes(this.graph.type)) return
            this.flags.show_legend = mode
            this.update_graph()
        });

        // Размер окна
        Event.listen('window-resized', () => {
            if (!this.constants.day_graph_types.includes(this.graph.type)) return
            if (this.highcharts_options) {
                let height = Math.max(window.innerHeight - 230, 500)
                if (this.mobile && this.graph.categories.length > 2) {
                    height += 50 * (this.graph.categories.length - 2)
                }

                this.highcharts_options.chart.height = height
                this.$forceUpdate()
            }
        });

        // Обновление дат
        Event.listen('set-dates', (dates) => {
            this.options.dates = [
                dates[0] ? this.start_of_day(dates[0]) : undefined,
                dates[1] ? this.end_of_day(dates[1]) : undefined
            ]

            this.$forceUpdate()
        })

        // Для экспорта
        Event.listen('set-export-chart', (data) => {
            this.options.export_chart = data
        });

        Event.listen('set-export-chart-extremes', (data) => {
            if (this.options.export_chart && this.options.export_chart.axes)
                this.options.export_chart.axes[0].setExtremes(data.start, data.end)
        });

    }

}
</script>

<style scoped>
.chart {
    overflow: visible;
    margin-left: -30px;
}
</style>