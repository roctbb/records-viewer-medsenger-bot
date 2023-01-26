<template>
    <div>
        <div class="container">
            <filter-panel :page="type == 'line' ? 'graph' : ( type == 'day-line' ? 'day-graph' :
      (group.categories && group.categories.includes('symptom') ? 'symptoms-' : '') + type )"
                          :disable_downloading="no_data || exporting" :patient="patient"/>
        </div>

        <!-- Ошибки -->
        <error-block :errors="errors" v-if="errors.length"/>

        <!-- Основная часть -->
        <loading v-if="!loaded && !errors.length"/>
        <div v-else>
            <div v-if="no_data" style="margin-top: 100px">
                <p style="text-align: center"><img :src="images.nothing_found"/></p>

                <p style="text-align: center">
                    <small>Нет данных за выбранный период.</small>
                </p>

            </div>

            <highcharts :constructor-type="'stockChart'" :options="options" style="margin-left: 30px" v-else/>

            <!-- Табличка -->
            <div class="container center" v-if="type == 'line' && this.statistics.length  && !no_data">
                <h5 class="text-center">Значения параметров за выбранный период</h5>

                <table class="table table-hover table-striped" v-if="!mobile">
                    <colgroup>
                        <col span="1" style="width: 55%;">
                        <col span="1" style="width: 15%;">
                        <col span="1" style="width: 15%;">
                        <col span="1" style="width: 15%;">
                    </colgroup>

                    <thead>
                    <tr>
                        <th scope="col" class="bg-info text-light">Параметр</th>
                        <th scope="col" class="bg-info text-light">Среднее</th>
                        <th scope="col" class="bg-info text-light">Мин</th>
                        <th scope="col" class="bg-info text-light">Макс</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr v-for="stat in this.statistics">
                        <th scope="row" style="text-align: left;">{{ stat.name }}</th>
                        <td>{{ stat.avg.toFixed(2) * 1 }}</td>
                        <td>{{ stat.min.toFixed(2) * 1 }}</td>
                        <td>{{ stat.max.toFixed(2) * 1 }}</td>
                    </tr>
                    </tbody>
                </table>

                <div v-else-if="type == 'line'" v-for="stat in this.statistics">
                    <hr>
                    <h6 class="text-center">{{ stat.name }}</h6>
                    <table class="table table-hover table-striped">
                        <thead>
                        <tr>
                            <th scope="col" class="bg-info text-light">Среднее</th>
                            <th scope="col" class="bg-info text-light">Мин</th>
                            <th scope="col" class="bg-info text-light">Макс</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr>
                            <td>{{ stat.avg.toFixed(2) * 1 }}</td>
                            <td>{{ stat.min.toFixed(2) * 1 }}</td>
                            <td>{{ stat.max.toFixed(2) * 1 }}</td>
                        </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Табличка с симптомами -->
            <div class="container center" v-if="type == 'line' && !no_data ">
                <h5 class="text-center">Симптомы и события</h5>
                <records-list :data="list_data"/>
            </div>
            <!-- Для экспорта -->
            <div v-show="false">
                <div ref="to-export">
                    <h4>Отчет по мониторингу пациента {{ patient.name }} ({{ patient.birthday }})</h4>
                    <span><strong>Период: </strong>
          {{
                            dates[0] ? ` с ${dates[0].toLocaleDateString()}` : ''
                        }} {{ dates[1] ? ` по ${dates[1].toLocaleDateString()}` : '' }}</span>
                    <hr>

                    <highcharts :constructor-type="'stockChart'" :options="export_options" style="margin-left: 20px"/>

                    <div class="container center" v-if="type == 'line' && this.statistics.length">
                        <h6>Значения параметров за выбранный период</h6>
                        <table class="table table-hover table-striped">
                            <colgroup>
                                <col span="1" style="width: 55%;">
                                <col span="1" style="width: 15%;">
                                <col span="1" style="width: 15%;">
                                <col span="1" style="width: 15%;">
                            </colgroup>
                            <thead>
                            <tr>
                                <th scope="col" class="bg-info text-light">Параметр</th>
                                <th scope="col" class="bg-info text-light">Среднее</th>
                                <th scope="col" class="bg-info text-light">Мин</th>
                                <th scope="col" class="bg-info text-light">Макс</th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr v-for="stat in this.statistics">
                                <th scope="row" style="text-align: left;">{{ stat.name }}</th>
                                <td>{{ stat.avg.toFixed(2) * 1 }}</td>
                                <td>{{ stat.min.toFixed(2) * 1 }}</td>
                                <td>{{ stat.max.toFixed(2) * 1 }}</td>
                            </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Табличка с симптомами -->


                </div>
            </div>

        </div>
    </div>
</template>

<script>
import {Chart} from 'highcharts-vue'
import Highcharts from "highcharts";
import stockInit from 'highcharts/modules/stock'
import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';
import 'vue2-datepicker/locale/ru';
import * as moment from "moment/moment";
import ErrorBlock from "./parts/ErrorBlock";
import Loading from "./parts/Loading";
import boost from "highcharts/modules/boost";
import heatmap from "highcharts/modules/heatmap";
import 'highcharts/modules/heatmap.src.js';
import FilterPanel from "./parts/FilterPanel";
import html2pdf from "html2pdf.js";
import arearange from 'highcharts/highcharts-more';
import RecordsList from "./parts/RecordsList";

stockInit(Highcharts)
heatmap(Highcharts);
boost(Highcharts)
arearange(Highcharts);

export default {
    name: "GraphPresenter",
    components: {RecordsList, FilterPanel, Loading, ErrorBlock, highcharts: Chart, DatePicker},
    props: ['patient'],
    data() {
        return {
            dates: [],
            errors: [],
            group: {},
            data: [],
            heatmap_data: {},
            collapsed_data: {},
            options: {},
            statistics: [],
            type: undefined,
            loaded: false,
            no_data: true,
            show_legend: true,
            collapse_points: undefined,
            exporting: false,
            export_options: {},
            export_chart: undefined,
            text_categories: ['symptom', 'medicine', 'patient_comment', 'information']
        }
    },
    computed: {
        list_data() {
            if (this.no_data) return undefined
            let records = []
            this.data.filter(graph => this.text_categories.includes(graph.category.name)).forEach(graph => {
                records = records.concat(graph.values.map(record => {
                    record.category_info = graph.category
                    record.formatted_date = moment(record.timestamp * 1000).format('HH:mm:ss DD.MM.YYYY')
                    record.date = moment(record.timestamp * 1000).format('DD.MM.YYYY')
                    return record
                }))
            })

            let dates = this.group_by(records, 'date')
            return Object.keys(dates).map(date => {
                return {
                    date: date,
                    records: dates[date]
                }
            })
        },
        offset() {
            return -1 * new Date().getTimezoneOffset() * 60
        },
        day() {
            return 24 * 36e5
        }
    },
    methods: {
        load_data: function (onload) {
            this.loaded = false
            this.no_data = true

            let group_tmp = this.group
            if (this.type.includes('line') && !this.group.categories.includes('symptom')) {
                group_tmp.categories = group_tmp.categories.concat(this.text_categories)
            }

            let data = {
                group_data: this.type == 'day-line',
                group: group_tmp,
                onload: onload,
                dates: {
                    start: this.dates[0] ? this.dates[0].valueOf() / 1000 : null,
                    end: this.dates[1] ? this.dates[1].valueOf() / 1000 : null,
                }
            }

            if (data.dates.start < data.dates.end || onload) {
                this.errors = []
                this.axios.post(this.url('/api/graph/group'), data).then(this.process_load_answer);
            }
        },

        process_load_answer: function (response) {
            this.data = response.data.data

            this.dates = [new Date(response.data.dates.start * 1000), new Date(response.data.dates.end * 1000)]
            Event.fire('set-dates', this.dates)

            // Собираю данные для суточных графиков
            if (this.type == 'day-line') {
                let tmp_data = []
                this.group.categories.forEach(category => {
                    if (this.text_categories.includes(category)) return

                    let category_data = {
                        category: undefined,
                        values: this.data.filter(record => record.category_info.name == category)
                    }
                    if (category_data.values.length) {
                        category_data.category = category_data.values[0].category_info
                        category_data.values.forEach(value => {
                            value.comments = this.data.filter(record => record.group == value.group && record.category_info.name != category)
                        })
                        tmp_data.push(category_data)
                    }
                })
                this.data = tmp_data
            }

            let start = this.dates[0] ? this.dates[0].getTime() : undefined

            if (!start) {
                this.data.forEach(category => {
                    if (category.values.length) {
                        if (!start || start > category.values[0].timestamp * 1000)
                            start = category.values[0].timestamp * 1000
                        if (start > category.values[category.values.length - 1].timestamp * 1000)
                            start = category.values[category.values.length - 1].timestamp * 1000
                    }

                })
            }

            this.options = this.get_options()
            this.is_empty()

            if (!this.no_data) {
                this.export_options = this.get_options()
                this.export_options.chart.events.render = function (event) {
                    Event.fire('set-export-chart', this)
                }

                this.export_options.title.align = 'left'

                this.export_options.chart.width = 700
                this.export_options.chart.backgroundColor = '#ffffff'

                if (this.type.includes('line')) {
                    this.export_options.legend.width = '100%'
                    this.export_options.chart.height = 450

                    this.export_options.series.forEach(series => {
                        series.data.forEach(val => {
                            if (val.marker && val.marker.symbol && val.marker.symbol.includes('url')) {
                                val.marker.symbol = 'circle'
                                val.marker.fillColor = '#FF0000'
                            }
                        })
                    })
                } else {
                    this.export_options.xAxis.labels.style = {
                        fontSize: '10px'
                    }
                    this.export_options.yAxis[0].labels.style = {
                        fontSize: '10px'
                    }
                }
            }

            this.loaded = true
        },
        get_options: function () {
            let start = this.dates[0] ? this.dates[0].getTime() : undefined
            let end = this.dates[1] ? this.dates[1].getTime() + 2 * this.offset * 1000 : new Date()

            let options = {
                chart: this.get_chart(),
                series: [],
                title: {
                    text: this.group.title + (this.type == 'day-line' ? ' (сутки)' : '')
                },
                xAxis: {
                    type: 'datetime',
                    gridLineWidth: 1,
                    minorGridLineWidth: 2,
                    minorTickLength: 0,
                    minorTickInterval: this.day,
                    min: start,
                    max: end,
                    ordinal: false,
                    dateTimeLabelFormats: {
                        day: '%d.%m',
                        hour: '%H:%M'
                    }
                },
                yAxis: [
                    this.get_y_axis(0),
                    this.get_y_axis(1)
                ],
                tooltip: {
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
                    style: {
                        width: this.mobile ? Math.ceil(window.innerWidth * 0.8) + 'px' : undefined
                    },

                    positioner: function () {
                        return {x: 10, y: 10};
                    },
                    shadow: false,
                    backgroundColor: 'rgba(255,255,255,0.8)',

                    shared: true,
                    headerFormat: null
                },
                legend: {},
                plotOptions: {},
                rangeSelector: {
                    enabled: false,
                },
                navigator: {
                    enabled: this.type == 'line',
                },
                scrollbar: {
                    enabled: false
                }
            }

            if (this.type.includes('line')) {
                options.chart.height = `${Math.max(window.innerHeight - 100, 500)}px`

                options.colors = this.colors
                options.tooltip.formatter = undefined

                options.plotOptions = {
                    line: {
                        dataLabels: {
                            enabled: true
                        }
                    },
                    series: {
                        marker: {
                            lineWidth: 1,
                            lineColor: null,
                        }
                    }
                }
                options.legend = {
                    enabled: this.show_legend,
                    itemDistance: 70,
                    labelFormatter: function () {
                        return this.name
                    }
                }

                if (!this.mobile) {
                    options.tooltip.positioner = undefined
                } else {
                    options.chart.height += 100
                }

                let days = Math.ceil((this.dates[1] - this.dates[0]) / (1000 * 60 * 60 * 24))
                if (days > 6) {
                    let t = days > 365 ? 30 : (days > 100 ? 10 : (days > 50 ? 5 : (days > 14 ? 2 : 1)))

                    options.xAxis.tickPositioner = function (min, max) {
                        let interval = t * 24 * 36e5, ticks = [], count = 0;

                        while (min < max) {
                            ticks.push(min);
                            min += interval;
                            count++;
                        }

                        ticks.info = {
                            unitName: 'day',
                            count: 5,
                            higherRanks: {},
                            totalRange: interval * count
                        }
                        return ticks;
                    }
                    options.xAxis.labels = {
                        rotation: -45
                    }
                }

            } else {
                options.tooltip.pointFormatter = undefined
                options.tooltip.positioner = undefined

                options.colorAxis = {
                    stops: [
                        [0, '#50B432'], [0.1, '#fcff00'], [1, '#ed341b']
                    ],
                    min: 0,
                    max: 1,
                    startOnTick: false,
                    endOnTick: false,
                    labels: {
                        format: '{value}'
                    }
                }
            }

            options.series = this.get_series(options)

            if (this.type == 'heatmap') {
                let count = this.heatmap_data.categories.symptoms.length + this.heatmap_data.categories.medicines.length
                options.chart.height = count * 20 + 110

                options.yAxis[0].categories = this.heatmap_data.categories.symptoms
                options.yAxis[1].categories = this.heatmap_data.categories.medicines

                options.xAxis.labels = {
                    rotation: -45
                }
                options.xAxis.tickmarkPlacement = 'between'
                options.xAxis.tickPositioner = function (min, max) {
                    let interval = 24 * 36e5, ticks = [], count = 0;

                    while (min < max) {
                        ticks.push(min);
                        min += interval;
                        count++;
                    }

                    ticks.info = {
                        unitName: 'day',
                        count: 5,
                        higherRanks: {},
                        totalRange: interval * count
                    }


                    return ticks;
                }

                if (this.group.categories.includes('symptom')) {
                    options.yAxis[0].height = 20 * this.heatmap_data.categories.symptoms.length

                    options.yAxis[1].top = 20 * this.heatmap_data.categories.symptoms.length + 60
                    options.yAxis[1].height = 20 * this.heatmap_data.categories.medicines.length

                    if (!this.heatmap_data.show_medicines || !this.heatmap_data.categories.medicines.length) {
                        this.heatmap_data.axis = options.yAxis.splice(1, 2)
                        let count = this.heatmap_data.categories.medicines.length
                        options.chart.height -= count * 20
                    }
                } else {
                    options.yAxis.splice(0, 1)
                }
            }

            if (this.type == 'day-line') {
                options.xAxis.min = (moment('05:00:00', 'HH:mm:ss').unix() + this.offset) * 1000
                let max = moment('05:30:00', 'HH:mm:ss')
                options.xAxis.max = (max.unix() + this.offset) * 1000 + this.day
                options.yAxis.splice(1, 2)
            }

            if (this.type == 'line' && this.group.categories.includes('glukose'))
                this.set_bands(options)

            return options
        },
        get_series: function (options) {
            let series = []
            series = series.concat(this.get_text_series({
                name: 'symptom',
                description: 'Симптом',
                color: '#ad0eca',
                y: -3
            }))

            if (!(this.type == 'heatmap' && this.group.categories.includes('symptom') && !this.heatmap_data.show_medicines)) {
                series = series.concat(this.get_medicine_series())
            }
            if (this.type == 'heatmap') {
                this.heatmap_data.medicine_series = this.get_medicine_series()
            }

            if (this.type.includes('line')) {
                let graph_series = this.get_graph_series()

                let sum_graph = this.data.filter(g => g.category.default_representation == 'day_sum').length
                let too_much_points = graph_series.map(s => s.data.length).reduce((a, b) => a + b) > 500 && !sum_graph

                if (graph_series.length && too_much_points) Event.fire('show-collapse', true)
                else Event.fire('show-collapse', false)

                if (sum_graph) {
                    this.collapse(graph_series, this.collapse_sum_point, this.collapse_sum_series)
                    graph_series = this.collapsed_data
                }
                if (!this.collapse_points && this.collapse_points != undefined && too_much_points) {
                    this.errors = ['За данный период в медицинской карте присутствует слишком большое количество записей (> 500). ',
                        'Чтобы увидеть комментарии к точкам и симптомы, загрузите период с меньшим количеством записей или усредните значения.']
                    graph_series.forEach(s => {
                        s.data = s.data.map(d => [d.x, d.y])
                    })
                    options.plotOptions.line.dataLabels.enabled = false
                    this.collapse_points = false
                } else if ((this.collapse_points || this.collapse_points == undefined) && too_much_points) {
                    this.errors = ['За данный период в медицинской карте присутствует слишком большое количество записей (> 500). ',
                        'Для удобства мы усреднили значения. Усреднение можно убрать, воспользовавшись галочкой выше, но в таком случае значения будут недоступны.']
                    this.collapse(graph_series, this.collapse_ranges_point, this.collapse_ranges_series)
                    graph_series = this.collapsed_data

                    if (this.collapse_points == undefined) Event.fire('set-collapse-mode', true)
                    this.collapse_points = true

                    options.plotOptions.line.dataLabels.enabled = false
                }


                if (this.type != 'day-line') {
                    let comment_series = this.get_text_series({
                        name: 'patient_comment',
                        description: 'Комментарий',
                        color: '#0e17ca',
                        y: -5
                    })
                    let info_series = this.get_text_series({
                        name: 'information',
                        description: 'Общая информация',
                        color: '#00ffe1',
                        y: -7
                    })
                    series = comment_series.concat(series)
                    series = info_series.concat(series)
                    series = graph_series.concat(series)
                } else {
                    series = graph_series
                }

                if (this.mobile && series.length > 2)
                    options.chart.height += 50 * (options.series.length - 2)
            }

            return series
        },
        get_graph_series: function () {
            // меняю даты
            if (this.type == 'day-line') {
                this.data.forEach(graph => {
                    if (graph.category.type != 'string') {
                        graph.values.forEach(value => {
                            let date = moment.unix(value.timestamp)
                            value.date = date.format('DD.MM.YY')

                            let time = moment(date.format('HH:mm:ss'), 'HH:mm:ss')
                            if (time.hour() < 5) time.add(1, 'day')

                            value.timestamp = time.unix()
                        })
                    }
                })
            }

            return this.data.filter((graph) => graph.category.type != 'string').map((graph) => {
                let series_data = {
                    name: graph.category.description,
                    category_type: graph.category.type,
                    code: graph.category.name,
                    values: graph.values.sort((a, b) => b.timestamp - a.timestamp),
                    marker: 'circle',
                }

                return this.prepare_series(series_data)
            })
        },
        get_medicine_series: function () {
            let medicines = {}
            let series

            if (this.type == 'line') {
                let y = -5
                this.data.filter((graph) => graph.category.name == 'medicine').forEach((graph) => {
                    graph.values.forEach((medicine) => {
                        let dict = {
                            timestamp: medicine.timestamp,
                            dose: !medicine.params || medicine.params.dose == null ? '' : ` (${medicine.params.dose})`
                        }
                        if (medicine.value in medicines)
                            medicines[medicine.value].push(dict)
                        else
                            medicines[medicine.value] = [dict]
                    })
                });

                series = Object.entries(medicines).map(([medicine, values]) => {
                    let series_data = {
                        name: medicine,
                        code: 'medicine',
                        values: values,
                        marker: 'square',
                        y: y
                    }

                    y -= 4

                    return this.prepare_series(series_data)
                })
            } else if (this.type == 'heatmap') {
                let medicines = {}
                let y = 0;

                this.data.filter((graph) => graph.category.name == 'medicine').forEach((graph) => {
                    graph.values.forEach((medicine) => {
                        let x = new Date((medicine.timestamp) * 1000)
                        x.setHours(12, 0, 0)

                        let medicine_data = {
                            points: [{
                                time: new Date(medicine.timestamp * 1000),
                                dose: !medicine.params || medicine.params.dose == null ? '' : ` (${medicine.params.dose})`
                            }],
                            x: +x + this.offset * 1000,
                            description: `Прием препарата <strong>"${medicine.value}"</strong> в `,
                        }

                        if (medicine.value in medicines) {
                            let old = medicines[medicine.value].find(m => m.x == medicine_data.x)
                            if (old) {
                                old.points.push(medicine_data.points[0])
                            } else {
                                medicines[medicine.value].push(medicine_data)
                            }
                        } else {
                            medicines[medicine.value] = [medicine_data]
                        }
                    })
                });

                series = Object.entries(medicines).map(([medicine, medicine_data]) => {
                    medicine_data.forEach(data => {
                        data.points.sort((a, b) => {
                            return a.time < b.time ? -1 : a.time > b.time ? 1 : 0
                        })
                        data.points.forEach(p => {
                            data.description += `<br>• <strong>${this.format_time(p.time)}</strong> ${p.dose}`
                        })
                    })

                    let series_data = {
                        name: medicine,
                        code: 'medicine',
                        values: medicine_data,
                        y: y
                    }

                    y += 1
                    return this.prepare_series(series_data)
                });

                this.heatmap_data.medicine_series = series
                this.heatmap_data.categories.medicines = Object.keys(medicines)
            }

            return series
        },
        get_text_series: function (data) {
            let series = []

            if (this.type == 'line') {
                series = this.data.filter((graph) => graph.category.name == data.name).map((graph) => {
                    let series_data = {
                        name: data.description,
                        code: data.name,
                        color: data.color,
                        values: graph.values,
                        marker: 'triangle',
                        y: data.y
                    }

                    return this.prepare_series(series_data)
                })
            } else if (this.type == 'heatmap') {
                let symptoms = {}
                let y = 0;

                this.data.filter((graph) => graph.category.name == data.name).forEach((graph) => {
                    graph.values.forEach((symptom) => {
                        let x = new Date((symptom.timestamp) * 1000)
                        x.setHours(12, 0, 0)

                        let symptom_data = {
                            points: [{
                                time: new Date(symptom.timestamp * 1000),
                                description: symptom.value,
                            }],
                            color: symptom.params.color != null ? symptom.params.color : 0.7,
                            description: '',
                            x: +x + this.offset * 1000,
                        }

                        let symptom_group = symptom.params.symptom_group ? symptom.params.symptom_group : symptom.value

                        if (symptom_group in symptoms) {
                            let old = symptoms[symptom_group].find(s => s.x == symptom_data.x)
                            if (old) {
                                old.color = old.color > symptom_data.color ? old.color : symptom_data.color
                                old.points.push(symptom_data.points[0])
                            } else {
                                symptoms[symptom_group].push(symptom_data)
                            }
                        } else {
                            symptoms[symptom_group] = [symptom_data]
                        }
                    })
                });

                series = Object.entries(symptoms).map(([symptom, symptom_data]) => {
                    symptom_data.forEach(data => {
                        data.points.sort((a, b) => {
                            return a.time < b.time ? -1 : a.time > b.time ? 1 : 0
                        })
                        data.points.forEach(p => {
                            data.description += `• <strong>${this.format_time(p.time)}</strong> - ${p.description}<br>`
                        })
                    })

                    let series_data = {
                        name: symptom,
                        code: 'symptom',
                        values: symptom_data,
                        y: y
                    }

                    y += 1
                    return this.prepare_series(series_data)
                });

                this.heatmap_data.categories.symptoms = Object.keys(symptoms)
            }

            return series
        },
        prepare_series: function (data) {
            let series = {
                name: data.name,
                category_code: data.code,
                category_type: data.category_type,
                data: this.prepare_values(data),
                showInNavigator: false,
                states: {
                    inactive: {
                        opacity: 1,
                    }
                },
            }

            if (this.type.includes('line')) {
                series.marker = {
                    enabled: true,
                    radius: 4,
                    symbol: data.marker
                }

                series.dataGrouping = {
                    enabled: false
                }

                if (this.text_categories.includes(data.code)) {
                    series.yAxis = 1
                    series.lineWidth = 0
                    if (data.code != 'medicine') {
                        series.color = data.color
                        series.marker.radius = 5
                    }
                } else {
                    series.yAxis = 0
                    series.showInNavigator = true
                    series.dashStyle = this.type == 'day-line' ? undefined : 'ShortDot'
                    series.lineWidth = 3
                    if (this.type == 'day-line') {
                        series.states = {
                            hover: {
                                enabled: false
                            }
                        }
                        series.lineWidth = 0
                    }
                }
            } else {
                series.yAxis = +(this.group.categories.length == 2 && data.code == 'medicine')
                series.colsize = this.day
                series.connectNulls = true

                series.nullColor = 'rgba(80,180,50,0.5)'
                series.borderWidth = 1
                series.borderColor = '#555555'
            }

            return series
        }
        ,
        prepare_values: function (data) {
            let res
            if (this.type.includes('line')) {
                if (data.code == 'medicine') {
                    res = data.values.map((value) => {
                        return {
                            dataLabels: {
                                enabled: false,
                            },
                            x: (value.timestamp + this.offset) * 1000,
                            y: data.y,
                            comment: this.get_comment({
                                value: data.name + value.dose,
                                timestamp: value.timestamp
                            }, `Прием лекарства`),
                        }
                    })
                } else if (this.text_categories.includes(data.code)) {
                    res = data.values.map((value) => {
                        let x = new Date((value.timestamp) * 1000)
                        // x.setHours(12, 0, 0)
                        return {
                            dataLabels: {
                                enabled: false,
                            },
                            x: +x + this.offset * 1000,
                            y: data.y,
                            comment: this.get_comment(value, data.name),
                        }
                    })
                } else {
                    res = data.values.map((value) => {
                        let dl
                        if (this.type == 'day-line') {
                            dl = {
                                enabled: true,
                                formatter: function () {
                                    return `${value.value} (${value.date})`
                                }
                            }
                        }
                        return {
                            x: (value.timestamp + this.offset) * 1000,
                            y: value.value,
                            comment: this.get_comment(value, data.name),
                            dataLabels: dl,
                            marker: {
                                symbol: this.get_symbol(value),
                                lineColor: this.get_color(value),
                                radius: this.get_radius(value),
                            }
                        }
                    })
                }
            } else {
                if (data.code == 'symptom') {
                    res = data.values.map(value => {
                        let date = moment.unix(+value.x / 1000).format('DD.MM')
                        return {
                            dataLabels: {
                                enabled: true,
                                formatter: function () {
                                    return value.points.length != 1 ? value.points.length : ''
                                },
                            },
                            x: value.x,
                            y: data.y,
                            name: data.name,
                            value: value.color,
                            comment: `<strong>${date}</strong><br>${value.description}`,
                        }
                    })
                    res = this.fill_nulls(res, data.y)
                } else {
                    res = data.values.map(value => {
                        return {
                            dataLabels: {
                                enabled: true,
                                formatter: function () {
                                    return value.points.length
                                },
                            },
                            x: value.x,
                            y: data.y,
                            name: data.name,
                            color: '#d1f6f6',
                            comment: value.description,
                        }
                    })
                }
            }
            return res.reverse()
        }
        ,
        get_y_axis: function (index) {
            let axis = {
                gridLineWidth: 1,
                lineWidth: 2,
                resize: {
                    enabled: true
                }
            }

            if (this.type.includes('line')) {
                axis.title = {
                    text: index ? 'События' : 'Значения'
                }

                axis.labels = {
                    align: 'right',
                    x: -5,
                    enabled: !index
                }
                axis.height = index ? '15%' : '80%'
                if (index) axis.top = '85%'
                if (this.type == 'day-line') axis.height = '100%'
            } else {
                axis.title = {
                    text: index ? 'Лекарства' : 'Симптомы'
                }

                axis.labels = {
                    align: 'left',
                    y: 5,
                    reserveSpace: true
                }

                axis.height = index ? '100%' : '70%'
                axis.top = '0%'
                axis.offset = 0
            }

            return axis
        },
        get_chart: function () {
            let chart = {
                type: this.type != 'day-line' && this.type != 'line' ? this.type : undefined,
                boostThreshold: 500,
                turboThreshold: 0,
                animation: false,
                zoomType: '',
                backgroundColor: "#fcfcfc",
                height: `${window.innerHeight - 100}`,
                width: `${window.innerWidth - 30}`,
                renderTo: 'container',
                events: {}
            }

            if (this.type == 'line') {
                chart.events = {
                    render: function (event) {
                        let stats = []

                        let binary_search = function (arr, value, l, r) {
                            let mid = Math.floor((r - l) / 2) + l

                            if (arr[mid] == value)
                                return mid;
                            if (r - l == 0)
                                return r + (arr[r] < value ? 1 : 0);
                            if (arr[mid] < value) {
                                l = (mid + 1) > r ? r : (mid + 1)
                                return binary_search(arr, value, l, r);
                            }
                            r = (mid - 1) < l ? l : (mid - 1)
                            return binary_search(arr, value, l, r);
                        }

                        let find_visible_data = function (data) {
                            const start = event.target.axes[0].min
                            const end = event.target.axes[0].max

                            let timestamps = data.map(point => point.x)

                            let start_index = binary_search(timestamps, start, 0, data.length - 1)
                            let end_index = binary_search(timestamps, end, 0, data.length - 1)

                            return data.slice(start_index, end_index).map(point => point.y)
                        }

                        this.series.filter(series => series.userOptions.yAxis == 0 && series.userOptions.type != 'arearange').forEach(series => {
                            let data = find_visible_data(series.data)

                            if (data.length) {
                                // calculate statistics for visible points
                                const max = data.reduce((a, b) => Math.max(a, b))
                                const min = data.reduce((a, b) => Math.min(a, b))
                                let average = data.reduce((a, b) => a + b, 0) / data.length

                                if (series.options.category_type == 'integer') {
                                    average = Math.ceil(average)
                                }

                                if (data.length > 0) {
                                    stats.push({
                                        name: series.name,
                                        code: series.options.category_code,
                                        data: data,
                                        avg: average,
                                        min: min,
                                        max: max
                                    })
                                }
                            }
                        });

                        // Для давления
                        let systolic_pressure = stats.find(st => st.code == 'systolic_pressure')
                        let diastolic_pressure = stats.find(st => st.code == 'diastolic_pressure')

                        if (systolic_pressure != null && diastolic_pressure != null) {
                            let pp_data = []
                            let map_data = []
                            systolic_pressure.data.forEach((s, index) => {
                                let d = diastolic_pressure.data[index]
                                map_data.push((s - d) / 3 + d)
                                pp_data.push(s - d)
                            })

                            stats.push({
                                name: 'Среднее давление (MAP)',
                                code: 'map',
                                avg: Math.ceil(map_data.reduce((a, b) => a + b, 0) / map_data.length),
                                min: Math.ceil(map_data.reduce((a, b) => Math.min(a, b))),
                                max: Math.ceil(map_data.reduce((a, b) => Math.max(a, b)))
                            })

                            stats.push({
                                name: 'Пульсовое давление',
                                code: 'pulse_pressure',
                                avg: Math.ceil(pp_data.reduce((a, b) => a + b, 0) / pp_data.length),
                                min: Math.ceil(pp_data.reduce((a, b) => Math.min(a, b))),
                                max: Math.ceil(pp_data.reduce((a, b) => Math.max(a, b)))
                            })
                        }

                        Event.fire('refresh-stats', stats)
                        Event.fire('set-export-chart-extremes', {
                            start: event.target.axes[0].min,
                            end: event.target.axes[0].max
                        })
                    }
                }
            }

            return chart
        },
        set_bands: function (options) {
            options.yAxis[0].plotBands = [{
                from: 0,
                to: 3,
                color: "rgba(255,117,117,0.25)"
            }, {
                from: 18,
                to: 100,
                color: "rgba(255,117,117,0.25)"
            }, {
                from: 3,
                to: 4,
                color: "rgba(255,209,117,0.25)"
            }, {
                from: 12,
                to: 18,
                color: "rgba(255,209,117,0.25)"
            }, {
                from: 4,
                to: 12,
                color: "rgba(186,255,117,0.25)"
            }]

            let min = null, max = null

            this.axios.get(this.url('/params')).then(response => {
                response.data.forEach(param => {
                    if (param.name && param.value != null) {
                        if (param.code == 'min_glukose' && (min == null || min > param.value))
                            min = param.value
                        if (param.code == 'max_glukose' && (max == null || max < param.value))
                            max = param.value
                    }
                })

                if (min != null) {
                    options.yAxis[0].plotBands[2].to = min
                    options.yAxis[0].plotBands[4].from = min
                }
                if (max != null) {
                    options.yAxis[0].plotBands[3].from = max
                    options.yAxis[0].plotBands[4].to = max
                }
            });
        },

        // Вспомогательные
        get_color: function (point) {
            if (point.additions) {
                return '#FF0000';
            }
            return undefined;
        },
        get_symbol: function (point) {
            if (point.additions) {
                return 'url(' + this.images.warning + ')'
            }
            return undefined;
        },
        get_radius: function (point) {
            if (point.additions) {
                return 6;
            }
            return undefined;
        },
        get_comment: function (point, category) {
            let date = new Date((point.timestamp) * 1000)
            let comment = `<strong>${this.type == 'day-line' ? point.date + ' ' : ''}${this.format_time(date)}</strong> - ${category}: ${point.value}`
            if (point.additions) {
                point.additions.forEach((value) => {
                    comment += `<br><strong style="color: red;">${value['addition']['comment']}</strong>`
                })
            }
            if (point.comments && point.comments.length) {
                comment += `<br><strong>Дополнительная информация:</strong>`
                point.comments.forEach((value) => {
                    comment += `<br>${value.value}`
                })
            }
            return comment
        },
        format_time: function (date) {
            return date.toTimeString().substr(0, 5)
        },
        format_date: function (date) {
            return date.toLocaleDateString()
        },
        is_empty: function () {
            this.options.series.forEach(s => {
                if (s.data.length) this.no_data = false
            })
            if (this.type == 'heatmap' && this.group.categories.includes('symptom') &&
                !this.heatmap_data.categories.symptoms.length) this.no_data = true
        },

        fill_nulls: function (data, y) {
            let start = moment(this.dates[0]).set({"hour": 12, "minute": 0, "second": 0}).add(this.offset, 'seconds')
            let end = moment(this.dates[1]).add(2, 'day').set({
                "hour": 12,
                "minute": 0,
                "second": 0
            }).add(this.offset, 'seconds')


            let i = 0
            let res = []

            while (end >= start) {
                if (i >= data.length || !end.isSame(moment.unix(data[i].x / 1000), 'day')) {
                    res.push({
                        dataLabels: {
                            enabled: true,
                            formatter: function () {
                                return ''
                            },
                        },
                        x: end.valueOf(),
                        y: y,
                        value: null,
                        comment: `<strong>${end.format('DD.MM')}</strong><br>Нет данных`,
                    })
                } else {
                    res.push(data[i])
                    i += 1
                }
                end.subtract(1, 'day')
            }
            return res
        },
        generate_report: function () {
            this.exporting = true

            let element = this.$refs['to-export']

            let opt = {
                margin: 0.5,
                filename: `${this.group.title}_${this.patient.name}.pdf`,
                page_break: {mode: 'css'},
                html2canvas: {dpi: 192, letterRendering: true},
                jsPDF: {unit: 'in', format: 'letter', orientation: 'portrait'}
            };
            setTimeout(() => {
                this.exporting = false;
            }, 5000);
            html2pdf().set(opt).from(element).save();
        },

        collapse: function (graph_series, point_handler, series_handler) {
            this.collapsed_data = []
            let by_hour = Math.ceil((this.dates[1] - this.dates[0]) / (1000 * 60 * 60 * 24)) < 4

            graph_series.forEach((graph, i) => {
                let data = []
                graph.data.forEach(val => {
                    let d = new Date(val.x - this.offset * 1000)
                    val.date = this.format_date(d)
                    if (by_hour) val.date += ` ${d.getHours()}:00`
                })

                let dates = new Set(graph.data.map(val => val.date))
                dates.forEach(date => {
                    let x_date = by_hour ? date : (date + ' 12:00')
                    let points = graph.data.filter(val => val.date == date)
                    let value = {
                        x: +moment(x_date, 'DD.MM.YYYY hh:mm') + this.offset * 1000,
                        marker: {
                            symbol: 'circle',
                            radius: 5
                        }
                    }
                    data.push(point_handler(value, points, date, graph))
                })

                series_handler(graph, data, i)
            })
        },
        collapse_sum_point: function (sum, points, date, graph) {
            sum.y = points.map(val => val.y).reduce((a, b) => a + b, 0)
            sum.comment = `<strong>${date}</strong> - ${graph.name}: ${sum.y}`
            return sum
        },
        collapse_sum_series: function (graph, data, i) {
            let series = {
                name: graph.name,
                type: 'line',
                category_code: graph.category_code,
                category_type: graph.category_type,
                data: data,
                yAxis: 0,
                showInNavigator: true,
                states: {
                    inactive: {
                        opacity: 1,
                    },
                },
                marker: {
                    enabled: true,
                    symbol: 'circle'
                },
                dataGrouping: {
                    enabled: false
                },
                lineWidth: 3,
                dashStyle: 'ShortDot'
            }

            this.collapsed_data.push(series)
        },
        collapse_ranges_point: function (median, points, date, graph) {
            median.count = points.length
            median.y = this.median(points.map(val => val.y))
            let low = Math.min.apply(Math, points.map(val => val.y))
            let high = Math.max.apply(Math, points.map(val => val.y))
            median.comment = `<strong>${graph.name}</strong><br>` +
                `<strong>Дата:</strong> ${date}<br>` +
                `<strong>Количество значений:</strong> ${points.length}<br>` +
                (low != high ? `<strong>Разброс значений:</strong> ${low} - ${high}<br>` : '') +
                `<strong>Медиана:</strong> ${median.y.toFixed(2) * 1}<br>`
            return {median: median, range: [median.x, low, high]}
        },
        collapse_ranges_series: function (graph, data, i) {
            let series = {
                name: graph.name,
                type: 'line',
                category_code: graph.category_code,
                category_type: graph.category_type,
                data: data.map(p => p.median),
                yAxis: 0,
                showInNavigator: true,
                color: this.colors[i],
                states: {
                    inactive: {
                        opacity: 1,
                    },
                },
                marker: {
                    enabled: true,
                    symbol: 'circle'
                },
                dataGrouping: {
                    enabled: false
                },
                lineWidth: 3,
                dashStyle: 'ShortDot'
            }

            this.collapsed_data.push(Object.assign({}, series))
            series.type = 'arearange'
            series.data = data.map(p => p.range)
            series.dashStyle = 'Solid'
            series.marker.radius = 4
            series.linkedTo = ':previous'
            series.opacity = 0.2
            series.states = {
                inactive: {
                    opacity: 0.2,
                },
                hover: {
                    opacity: 0.5
                }
            }
            this.collapsed_data.push(series)
        },

        median: function (arr) {
            const arrayHalf = arr.length / 2
            const sorted = [].concat(arr).sort((a, b) => a - b)

            return arr.length % 2 === 0
                ? (sorted[arrayHalf] + sorted[arrayHalf + 1]) / 2
                : sorted[~~(arrayHalf)]
        }
    },
    created() {
        this.dates = {
            range: [],
            period: 14
        }

        this.colors = ['#058DC7', '#50B432', '#aa27ce', '#fcff00',
            '#24CBE5', '#64E572', '#c355ff', '#fce200', '#6AF9C4']

        Highcharts.setOptions({
            lang: {
                loading: 'Загрузка...',
                months: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
                weekdays: ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'],
                shortMonths: ['Янв', 'Фев', 'Март', 'Апр', 'Май', 'Июнь', 'Июль', 'Авг', 'Сент', 'Окт', 'Нояб', 'Дек'],
                exportButtonTitle: "Экспорт",
                printButtonTitle: "Печать",
                rangeSelectorFrom: "С",
                rangeSelectorTo: "По",
                rangeSelectorZoom: "Период",
                downloadPNG: 'Скачать PNG',
                downloadJPEG: 'Скачать JPEG',
                downloadPDF: 'Скачать PDF',
                downloadSVG: 'Скачать SVG',
                printChart: 'Напечатать график',
                resetZoom: 'Весь график'
            }
        });

        Event.listen('set-export-chart', (data) => {
            this.export_chart = data
        })
        Event.listen('set-export-chart-extremes', (data) => {
            if (this.export_chart && this.export_chart.axes)
                this.export_chart.axes[0].setExtremes(data.start, data.end)
        });

        Event.listen('load-graph', (data) => {
            this.type = 'line'
            this.group = data.group
            this.dates = data.dates
            this.load_data(data.onload)
        });

        Event.listen('load-day-graph', (data) => {
            this.type = 'day-line'
            this.group = data.group
            this.dates = [undefined, new Date(moment('23:59:59', 'HH:mm:ss').unix() * 1000)]
            this.load_data()
        });

        Event.listen('load-heatmap', (data) => {
            this.type = 'heatmap'
            this.group = data.group
            this.dates = data.dates

            this.heatmap_data = {
                medicine_series: [],
                categories: {
                    symptoms: [],
                    medicines: []
                },
                show_medicines: false
            }

            this.load_data(data.onload)
        });

        Event.listen('refresh-stats', (stats) => {
            this.statistics = stats
        })

        Event.listen('window-resized', () => {
                if (this.options.chart) {
                    this.options.chart.width = window.innerWidth - 30
                    if (this.type.includes('heatmap')) {
                        let count = this.heatmap_data.categories.symptoms.length + this.heatmap_data.categories.medicines.length
                        this.options.chart.height = count * 20 + 110

                        if (this.group.categories.includes('symptom')) {
                            this.options.yAxis[0].height = 20 * this.heatmap_data.categories.symptoms.length

                            if (this.options.yAxis[1]) {
                                this.options.yAxis[1].top = 20 * this.heatmap_data.categories.symptoms.length + 60
                                this.options.yAxis[1].height = 20 * this.heatmap_data.categories.medicines.length
                            }

                            if (!this.heatmap_data.show_medicines || !this.heatmap_data.categories.medicines.length) {
                                let count = this.heatmap_data.categories.medicines.length
                                this.options.chart.height -= count * 20
                            }
                        }
                    } else {
                        this.options.chart.height = Math.max(window.innerHeight - 100, 500)
                        if (this.mobile && this.options.series.length > 2) {
                            this.options.chart.height += 50 * (this.options.series.length - 2)
                        }
                    }
                }
            }
        );

        Event.listen('back-to-dashboard', () => {
            this.loaded = false;
            this.collapse_points = undefined
            window.OBJECT_ID = undefined;
        });

        Event.listen('graph-update-dates', (dates) => {
            this.dates = dates
            this.load_data()
        });

        Event.listen('update-points', (mode) => {
            this.load_data()
            this.collapse_points = mode
            this.$forceUpdate()
        });

        Event.listen('update-legend', (mode) => {
            this.show_legend = mode
            if (this.options)
                this.options.legend.enabled = mode
        });

        Event.listen('update-medicines', (mode) => {
            this.heatmap_data.show_medicines = !mode
            this.load_data()
        });

        Event.listen('incorrect-dates', (duration) => {
            if (duration < 0 && this.errors[0] != '<strong>Выбран некорректный период</strong>')
                this.errors.unshift('<strong>Выбран некорректный период</strong>')
            else if (duration > 30 && this.errors[0] != 'Пожалуйста, выберите период <strong>не больше</strong> 30 дней.')
                this.errors.unshift('Пожалуйста, выберите период <strong>не больше</strong> 30 дней.')
        })

        Event.listen('generate-report', () => {
            if (this.loaded)
                this.generate_report()
        })
    }
}
</script>

<style scoped>
.table {
    table-layout: fixed;
    width: 100%;
    text-align: center;
    font-size: 0.8rem;
}

.container {
    padding: 5px 10px 5px 0;
}

.row {
    grid-column-gap: 10px;
    margin-bottom: 5px;
}

table tr {
    break-inside: avoid;
}
</style>
