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
    name: "LineGraph",
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
                show_sma: false,
                show_median: false,
                show_colors: false
            },
            highcharts_options: {},
            export_options: {},
            options: {
                text_categories: ['symptom', 'medicine', 'patient_comment', 'information', 'side_effect'],
                colors: [],
                dates: []
            },
            series: {
                clear: undefined,
                collapsed: undefined,
                sum: undefined,
                sma: undefined,
                median: undefined,
                colors: undefined,
                common: undefined
            },
            records: {
                all: undefined,
                by_categories: undefined,
                additional: undefined
            }
        }
    },
    computed: {
        by_hours() {
            return Math.ceil((this.options.dates[1] - this.options.dates[0]) / this.day) < 4
        },
        sum_graph() {
            return this.records.all &&
                this.records.all
                    .filter(record => record.category_info.default_representation == 'day_sum')
                    .length
        },
        too_much_points() {
            return this.records.all &&
                this.records.all.length > 500 && !this.sum_graph
        }
    },
    methods: {
        reset_view: function () {
            this.flags.ready = false

            this.series = {
                clear: undefined,
                collapsed: undefined,
                sum: undefined,
                sma: undefined,
                median: undefined,
                colors: undefined,
                common: undefined
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
        check_additional: function () {
            if (this.flags.show_sma && !this.records.additional) {
                this.load_additional_data(this.graph.categories,
                    this.options.dates[0].getTime(), 7, 'line')
                return false
            }
            return true
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
                })
            })

        },
        set_line_graph_options: function () {
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

            // y axis 0
            this.highcharts_options.yAxis[0].title = {text: 'Значения'}
            this.highcharts_options.yAxis[0].offset = 5
            this.highcharts_options.yAxis[0].labels = {
                align: 'right',
                x: -5,
                rotation: 0,
                enabled: true
            }
            this.highcharts_options.yAxis[0].height = '80%'

            // y axis 1
            this.highcharts_options.yAxis[1].title = {text: 'События'} //, offset: 20, x: -15}
            this.highcharts_options.yAxis[1].offset = 5
            this.highcharts_options.yAxis[1].labels = {enabled: false}
            this.highcharts_options.yAxis[1].height = '15%'
            this.highcharts_options.yAxis[1].top = '85%'

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
            if (!this.check_additional()) return undefined
            let series = this.get_number_series()

            let common = this.series.common
            if (!common) {
                common = this.get_text_series()
                common = common.concat(this.get_medicine_series())
                this.series.common = common
            }

            series = series.concat(common)
            series = series.filter((s) => s != undefined)

            return series
        },
        get_text_series: function () {
            let series = []
            let text_categories = [{
                name: 'symptom',
                description: 'Симптом',
                color: this.colors.orange[1],
                marker: 'triangle',
                y: -2
            }, {
                name: 'information',
                description: 'Общая информация',
                color: this.colors.purple[1],
                marker: 'triangle',
                y: -4
            }, {
                name: 'side_effect',
                description: 'Побочный эффект',
                color: this.colors.red[1],
                marker: 'triangle',
                y: -0
            }, {
                name: 'comment',
                description: 'Комментарий пациента',
                color: this.colors.blue[1],
                marker: 'triangle',
                y: -6
            }]

            text_categories.forEach((category) => {
                series.push(this.prepare_series(category))
            })

            return series
        },
        get_medicine_series: function () {
            if (!this.records.by_categories['medicine']) return []
            let series = []

            let records_by_medicine_name = this.group_by(this.records.by_categories['medicine'], 'value')

            let y = -6
            Object.entries(records_by_medicine_name).forEach(([medicine, records]) => {
                records.forEach((rec) => {
                    if (rec.params && rec.params.dose) rec.dose = ` (${rec.params.dose})`
                })

                series.push(this.prepare_series({
                        name: 'medicine',
                        description: 'Прием препарата ' + medicine,
                        marker: 'square',
                        y: y,
                        records: records
                    })
                )
                y -= 4
            })

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

            let check_collapse = (rule, series, point_handler, series_handler) => {
                if (!this.series[rule]) {
                    series = this.collapse(series, point_handler, series_handler)
                    this.series[rule] = series
                } else {
                    series = this.series[rule]
                }

                return series
            }

            // Схлопывание графиков
            this.highcharts_options.plotOptions.line.dataLabels.enabled = true
            if (this.sum_graph) {
                series = check_collapse('sum', series, this.collapse_sum_point, this.collapse_sum_series)
            } else if (this.flags.show_sma) {
                series = check_collapse('sma', series, this.collapse_sma_ranges_point, this.collapse_sma_ranges_series)
            } else if (this.flags.show_median) {
                series = check_collapse('median', series, this.collapse_median_ranges_point, this.collapse_median_ranges_series)
            } else if (this.flags.show_colors) {
                if (!this.series.colors) {
                    series = get_clear_series()
                    this.series.colors = series
                } else {
                    series = this.series.colors
                }
            } else if (this.too_much_points) {
                Event.fire('update-graph-view-errors', ['too_mach_points', 'not_averaged'])

                if (!this.series.collapsed) {
                    series.forEach(s => {
                        s.data = s.data.map(d => [d.x, d.y])
                        s.marker.radius = 2
                    })
                    this.series.collapsed = series
                } else {
                    series = this.series.collapsed
                }
                this.highcharts_options.plotOptions.line.dataLabels.enabled = false
            }

            return series
        },

        prepare_series: function (data) {
            if (!data.records)
                data.records = this.records.by_categories[data.name]

            if (!data.records) return undefined

            data.records = data.records.sort((a, b) => a.timestamp - b.timestamp)

            data.category_type = data.records[0].category_type
            data.is_text_category = data.category_type == 'string'

            let series = {
                name: data.description,
                category_code: data.name,
                category_type: data.category_type,
                data: this.prepare_values(data),
                showInNavigator: !data.is_text_category,
                states: {
                    inactive: {opacity: 1}
                },
                marker: {
                    enabled: true,
                    radius: 4,
                    symbol: data.marker
                },
                dataGrouping: {enabled: false},
            }

            if (data.is_text_category) {
                series.yAxis = 1
                series.lineWidth = 0
                series.line = {visible: false}
                if (data.code != 'medicine') {
                    series.color = data.color
                    series.marker.radius = 5
                }
            } else {
                series.yAxis = 0
                series.showInNavigator = true
                series.dashStyle = 'ShortDot'
                series.lineWidth = 2
            }

            return series
        },
        prepare_values: function (data) {
            let res

            let get_point_template = (rec) => {
                return {
                    dataLabels: {enabled: false},
                    x: +new Date(rec.timestamp * 1000),
                    y: data.y,
                    timestamp: rec.timestamp,
                    formatted_date: rec.formatted_date,
                    formatted_time: rec.formatted_time,
                    formatted_hours: rec.formatted_hours,
                    comment: this.get_comment(rec, data.description)
                }
            }

            // Препараты
            if (data.name == 'medicine') {
                res = data.records.map((rec) => {
                    let point = get_point_template(rec)
                    point.value = data.description + rec.dose
                    point.comment = this.get_comment(point, `Прием препарата`)

                    return point
                })
                // Текстовые
            } else if (data.is_text_category) {
                res = data.records.map((rec) => {
                    return get_point_template(rec)
                })
                // Значения
            } else {
                res = data.records.map((rec) => {
                    let point = get_point_template(rec)
                    point.dataLabels = undefined
                    point.y = rec.value
                    point.value = rec.value
                    point.marker = this.get_marker(rec)
                    return point
                })
            }

            return res
        },

        // Схлопывание
        collapse: function (series, point_handler, series_handler) {
            let collapsed = []

            series.forEach((graph, i) => {
                let data = []
                graph.data.forEach(val => {
                    val.collapse_date = this.by_hours ? val.formatted_hours : val.formatted_date
                })

                let data_by_dates = this.group_by(graph.data, 'collapse_date')

                Object.entries(data_by_dates).forEach(([date, values]) => {
                    let x_date = this.by_hours ? date : (date + ' 12:00')
                    let points = values

                    let value = {
                        x: +moment(x_date, 'DD.MM.YYYY hh:mm'),
                        marker: {
                            symbol: 'circle',
                            radius: 5
                        }
                    }
                    data.push(point_handler(value, points, date, graph, data_by_dates))
                })

                collapsed = collapsed.concat(series_handler(graph, data, i))
            })
            return collapsed
        },
        collapse_sum_point: function (sum, points, date, graph, data_by_dates) {
            sum.y = Math.round(points.map(val => val.y).reduce((a, b) => a + b, 0))
            sum.comment = `<b>${date}</b> - ${graph.name}: ${sum.y}`
            return sum
        },
        collapse_sum_series: function (graph, data, i) {
            let series = {}
            this.copy(series, graph)
            series.data = data

            return [series]
        },
        collapse_median_ranges_point: function (median, points, date, graph, data_by_dates) {
            median.count = points.length
            median.y = this.median(points.map(val => val.y))

            let low = Math.min.apply(Math, points.map(val => val.y))
            let high = Math.max.apply(Math, points.map(val => val.y))
            median.comment = `<u>${graph.name}</u><br>` +
                `<b>Дата:</b> ${date}<br>` +
                `<b>Количество значений:</b> ${points.length}<br>` +
                (low != high ? `<b>Разброс значений:</b> ${low} - ${high}<br>` : '') +
                `<b>Медиана:</b> ${median.y.toFixed(2) * 1}<br>`
            return {median: median, range: [median.x, low, high]}
        },
        collapse_median_ranges_series: function (graph, data, i) {
            let series = {}
            let range_series = {}
            this.copy(series, graph)

            series.name += (' (Медиана)')
            series.data = data.map((p) => p.median)
            series.dashStyle = 'Solid'
            series.color = this.options.colors[i]

            this.copy(range_series, series)
            range_series.type = 'arearange'
            range_series.marker.radius = 0
            range_series.data = data.map((p) => p.range)
            range_series.linkedTo = ':previous'
            range_series.fillOpacity = 0.5
            range_series.opacity = 0.2
            range_series.states = {
                inactive: {opacity: 0.2},
                hover: {opacity: 0.5}
            }
            return [series, range_series]
        },
        collapse_sma_ranges_point: function (sma, points, date, graph, data_by_dates) {
            sma.count = points.length
            let additional = this.records.additional && this.records.additional[graph.category_code] ? this.records.additional[graph.category_code] : []
            let result = this.simple_moving_average(data_by_dates, additional, 7, date)

            if (!result.credible) {
                sma.marker.enabled = false
            }

            if (result.filled_days == 0) {
                result.value = points.map(val => val.y).reduce((a, b) => a + b, 0) / points.length
            }

            sma.y = +result.value.toFixed(2)

            let low = Math.min.apply(Math, points.map(val => val.y))
            let high = Math.max.apply(Math, points.map(val => val.y))

            sma.comment = `<b>${graph.name}</b><br>` +
                `<b>Дата:</b> ${date}<br>` +
                `<b>Количество значений за день:</b> ${points.length}<br>` +
                (low != high ? `<b>Разброс значений:</b> ${low} - ${high}<br>` : '') +
                `<b>Среднее${result.filled_days == 0 ? ' за день' : ' скользящее за 7 дней'}:</b> ${sma.y}<br>` +
                (!result.credible ? `<b style="color: red">Ненадежный показатель</b> – данные за ${result.filled_days} дн.<br>` : '')
            return {sma: sma, range: [sma.x, low, high]}

        },
        collapse_sma_ranges_series: function (graph, data, i) {
            let series = {}
            let range_series = {}
            this.copy(series, graph)

            series.name += (' (Среднее скользящее за 7 дней)')
            series.data = data.map((p) => p.sma)
            series.type = 'spline'
            series.dashStyle = 'Solid'
            series.color = this.options.colors[i]

            this.copy(range_series, series)
            range_series.type = 'arearange'
            range_series.marker.radius = 0
            range_series.data = data.map((p) => p.range)
            range_series.linkedTo = ':previous'
            range_series.fillOpacity = 0.5
            range_series.opacity = 0.2
            range_series.states = {
                inactive: {opacity: 0.2},
                hover: {opacity: 0.5}
            }
            return [series, range_series]
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
        Event.listen('draw-graph', (options) => {
            if (!this.constants.graph_types.includes(this.graph.type)) return
            this.reset_view()

            this.records.all = this.data.all
            this.records.by_categories = this.data.by_categories
            this.records.additional = undefined

            if (this.too_much_points) {
                this.flags.show_median = true
                Event.fire('set-points-mode', {mode: true, target: 'median'})
            }

            this.copy(this.highcharts_options, options)
            this.set_line_graph_options()
        })

        // Дополнительные записи
        Event.listen('additional-loaded', (data) => {
            this.records.additional = this.group_records_by_categories_by_dates(data)
            this.update_graph()
        })

        // Режимы отображения
        Event.listen('update-legend', (mode) => {
            if (!this.constants.graph_types.includes(this.graph.type)) return
            this.flags.show_legend = mode
            this.update_graph()
        });

        Event.listen('update-points', (data) => {
            this.flags['show_' + data.target] = data.mode

            if (data.mode) {
                Array('median', 'sma', 'colors').forEach((m) => {
                    if (data.target != m && this.flags['show_' + m]) {
                        this.flags['show_' + m] = false
                        Event.fire('set-points-mode', {mode: false, target: m})
                    }
                })
            }

            this.update_graph()
        });

        // Размер окна
        Event.listen('window-resized', () => {
            if (!this.constants.graph_types.includes(this.graph.type)) return
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