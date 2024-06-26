<template>
    <div v-if="options.report">
        <h4>{{ options.report.title }}</h4>
        <filter-panel page="formalized-report" :patient="patient"
                      :disable_downloading="false" :last_date="last_date"/>

        <!-- Ошибки -->
        <error-block :errors="errors" v-if="errors.length"/>
        <loading v-if="!options.loaded"/>
        <nothing-found v-else-if="no_data"/>
        <div v-else>

            <!-- Описание -->
            <div style="margin-top: 15px;" class="alert alert-info" role="alert"
                 v-if="options.report.options.description">
                <span v-html="options.report.options.description"/>
            </div>

            <!-- Блоки -->
            <report-block :block="block" :data="block_data" :report="options.report.options"
                          :key="'block-' + i"
                          v-for="(block, i) in options.report.options.blocks"/>

            <!-- Для экспорта -->
            <div v-show="false" v-if="options.loaded">
                <div ref="to-export">
                    <h4>{{ options.report.title }}</h4>
                    <h6>Пациент: {{ patient.name }} ({{ patient.birthday }})</h6>
                    <span><b>Период: </b>{{
                            options.dates[0] ? ` с ${options.dates[0].toLocaleDateString()}` : ''
                        }} {{ options.dates[1] ? ` по ${options.dates[1].toLocaleDateString()}` : '' }}</span>
                    <hr>
                    <!-- Описание -->
                    <div class="alert alert-info" role="alert"
                         v-if="options.report.options.description">
                        <span v-html="options.report.options.description"/>
                    </div>
                    <!-- Блоки -->
                    <report-block :block="block" :data="block_data" :report="options.report.options"
                                  :key="'export-block-' + i" :to_export="true" style="page-break-inside: avoid;"
                                  v-for="(block, i) in options.report.options.blocks"/>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
import FilterPanel from "../../common/FilterPanel.vue";
import html2pdf from "html2pdf.js";
import Loading from "../../common/Loading.vue";
import ErrorBlock from "../../common/ErrorBlock.vue";
import ReportBlock from "./parts/ReportBlock.vue";
import NothingFound from "../../common/NothingFound.vue";

export default {
    name: "FormalizedReport",
    components: {NothingFound, ReportBlock, Loading, FilterPanel, ErrorBlock},
    props: {
        patient: {required: true},
        last_date: {required: true},
        params: {required: false}
    },
    data() {
        return {
            options: {
                loaded: false,
                report: undefined,
                dates: undefined,
                period: undefined,
                data_format_codes: undefined,
                report_status_codes: undefined
            },
            data: {
                records: [],
                records_by_categories: {},
                records_by_dates: {},
                records_by_categories_by_dates: {},
                additional_records: [],
                prescriptions: {}
            },
            stats: {
                sma: undefined,
                zones: undefined,
                compliance: undefined
            },
            errors: [],
        }
    },
    computed: {
        block_data() {
            return {
                dates: this.options.dates,
                period: this.options.period,
                data: this.data,
                stats: this.stats,
                params: this.params,
                type: 'formalized-report'
            }
        },
        no_data() {
            if (!this.data.records) return true
            let records = this.data.records.filter((r) => this.options.report.required_categories.includes(r.category_code))
            return !records.length
        }
    },
    methods: {
        load: function () {
            this.options.loaded = false
            this.errors = []

            let categories = this.options.report.categories
            let dates = this.options.dates.map(date => date ? Math.round(date.getTime() / 1000) : date)
            let options = {
                type: 'formalized-report'
            }

            this.load_data(categories, dates, options)
        },
        load_report_status_codes: function () {
            let codes = {}

            this.options.report.options.statuses.forEach((status) => {
                status.rules.forEach((rule) => {
                    let categories = rule.conditions.map((c) => c.category)

                    if (!(rule.code in codes)) codes[rule.code] = new Set()
                    categories.forEach(codes[rule.code].add, codes[rule.code])
                })
            })

            Object.entries(codes).forEach(([code, categories]) => codes[code] = Array.from(categories))

            this.options.report_status_codes = codes
        },
        load_data_format_codes: function () {
            let codes = {}

            this.options.report.options.blocks.forEach((block) => {
                block.fields.forEach((field) => {
                    let categories = []
                    let parts = []

                    if (field.type == 'table') {
                        categories = field.record_groups ?
                            field.cols.filter((col) => col.code == 'category').map((col) => col.category) :
                            field.rows.map((row) => row.category)

                        parts = field.cols
                    }

                    if (field.type == 'message_list') {
                        categories = field.record_groups ?
                            field.message_parts.filter((part) => ['records_list', 'text', 'medicine_description'].includes(part.code)).map((part) => part.category) :
                            field.message_parts.map((part) => part.category)

                        categories = categories.filter((c) => c)

                        parts = field.message_parts
                    }

                    if (field.type == 'progress_bars') {
                        categories = field.bars.map((row) => row.category)
                        parts = field.parts
                    }

                    parts.forEach((part) => {
                        if (!(part.code in codes)) codes[part.code] = new Set()

                        categories.forEach(codes[part.code].add, codes[part.code])

                        if (part.code.includes('sma') && part.period) {
                            if (!this.stats.sma) this.stats.sma = {}
                            this.stats.sma.period = part.period
                        }

                        if (part.code.includes('zone')) {
                            if (!this.stats.zones) this.stats.zones = {}

                            categories.forEach((category) => {
                                if (!(category in this.stats.zones)) this.stats.zones[category] = {}
                                this.stats.zones[category][part.zone_index] = {
                                    color: part.color,
                                    zone_description: part.zone_description,
                                    count: 0,
                                    percent: 0
                                }
                            })
                        }
                    })

                })
            })

            Object.entries(codes).forEach(([code, categories]) => codes[code] = Array.from(categories))

            this.options.data_format_codes = codes
        },
        add_zones: function (records) {
            records.forEach(record => {
                if (record.category_code in this.stats.zones) {
                    let zone = this.zone_addition(record)
                    record.zone_index = zone ? zone.zone_index : 'Нет зоны'
                }
            })
        },
        add_comments: function (records) {
            let need_stats = 'count' in this.options.report_status_codes && this.options.report_status_codes.count.includes('algorithm_comments')
            if (need_stats)
                this.stats.count.algorithm_comments = {value: 0}

            records.forEach(record => {
                if (this.options.data_format_codes.algorithm_comments.includes(record.category_code)) {
                    let comment_additions = this.comment_additions(record)
                    record.comments = comment_additions.map((a) => a['addition']['comment'])

                    if (need_stats)
                        this.stats.count.algorithm_comments.value += record.comments.length
                }
            })
        },

        generate_report: function () {
            let element = this.$refs['to-export']

            let opt = {
                margin: [0.5, 0.25],
                filename: this.patient.name + '.pdf',
                page_break: {mode: 'css'},
                image: {type: "jpeg", quality: 1},
                html2canvas: {dpi: 300, letterRendering: true}, // useCORS: true
                jsPDF: {unit: 'in', format: 'a4', orientation: 'portrait'}
            };

            html2pdf().set(opt).from(element).save();
        },

        // values
        get_sma: function () {
            this.stats.sma = {period: this.stats.sma.period}
            this.options.data_format_codes.sma.forEach((category) => {
                this.stats.sma[category] = this.simple_moving_average(
                    this.data.records_by_categories_by_dates[category],
                    this.data.additional_records[category],
                    this.stats.sma.period, this.format_date(this.options.dates[1])
                )
            })

            /* sma structure
            * "category" : {
            *     value: ..,
            *     credible: ..,
            *     filled_days: ..
            * }
            */
            Event.fire('refresh-report-status')
        },
        get_zones_distribution: function () {
            Object.entries(this.stats.zones).forEach(([category, zones]) => {
                Object.entries(zones).forEach(([zone_index, zone]) => {
                    zone.count = 0
                    zone.percent = 0
                })
            })

            Object.entries(this.stats.zones).forEach(([category, zones]) => {
                if (!this.data.records_by_categories[category]) return

                let total_cnt = this.data.records_by_categories[category] ? this.data.records_by_categories[category].length : 0
                let records_by_zones = this.group_by(this.data.records_by_categories[category], 'zone_index')

                Object.entries(zones).forEach(([zone_index, zone]) => {
                    zone.count = records_by_zones[zone_index] ? records_by_zones[zone_index].length : 0
                    zone.percent = (zone.count / total_cnt) * 100
                })
            })

            /* zone structure
             * "category" : {
             *     zone_index: {
             *       color: ..,
             *       zone_description: ..,
             *       count: ..,
             *       percent: ..
             *   }
             * }
             */
            Event.fire('refresh-report-status')
        },

        get_stats: function () {
            Object.entries(this.options.report_status_codes).forEach(([code, categories]) => {
                if (code == 'max_grade') {
                    this.stats.max_grade = {}
                    categories.forEach((c) => {
                        let grades = this.data.records_by_categories[c] ?
                            this.data.records_by_categories[c].filter((r) => r.params && r.params.grade).map((r) => r.params.grade) :
                            []
                        this.stats.max_grade[c] = {value: grades.length ? Math.max(...grades) : undefined}
                    })
                }

                if (code == 'count') {
                    this.stats.count = {}
                }

            })
        }
    },
    mounted() {
        this.options.dates = [undefined, this.last_date]
    },
    created() {
        Event.listen('loaded', (data) => {
            if (data.info.type != 'formalized-report') return

            this.stats.sma = {period: this.stats.sma.period}
            this.stats.compliance = []

            this.data.records = data.records
            this.data.records_by_categories = this.group_by(data.records, 'category_code')
            this.data.records_by_categories_by_dates = this.group_records_by_categories_by_dates(this.data.records_by_categories, true)
            this.data.record_groups = this.get_record_groups(data.records, true)
            this.data.prescriptions = []

            this.get_stats()

            if ('zone_cnt' in this.options.data_format_codes ||
                'zone_percent' in this.options.data_format_codes) this.add_zones(data.records)

            if ('algorithm_comments' in this.options.data_format_codes) this.add_comments(data.records)

            Event.fire('set-dates', this.options.dates)
            this.options.period = this.dates_difference(this.options.dates[0], this.options.dates[1])

            if ('zone_cnt' in this.options.data_format_codes ||
                'zone_percent' in this.options.data_format_codes) this.get_zones_distribution()

            this.options.loaded = true

            if ('sma' in this.options.data_format_codes) {
                let period = Math.max(0, this.stats.sma.period - this.options.period + 1)

                this.load_additional_data(this.options.data_format_codes.sma, this.options.dates[0].getTime(),
                    period, 'formalized-report')
            }

            if ('medicine_description' in this.options.data_format_codes) {
                this.options.loaded = false

                this.send_order('get_medicines', 'FORMS', {
                    from_timestamp: Math.floor(this.options.dates[0].getTime() / 1000),
                    to_timestamp: Math.floor(this.options.dates[1].getTime() / 1000)
                }, 'prescriptions-loaded')
            }

            if ('compliance' in this.options.data_format_codes) {
                this.options.loaded = false

                this.send_order('get_compliance', window.AGENTS.FORMS_AGENT_ID, {
                    from_timestamp: Math.floor(this.options.dates[0].getTime() / 1000),
                    to_timestamp: Math.floor(this.options.dates[1].getTime() / 1000)
                }, 'compliance-loaded')
            }

            this.$forceUpdate()
        })

        Event.listen('additional-loaded', (data) => {
            if (!data || !this.options.report) return

            this.data.additional_records = this.group_records_by_categories_by_dates(data)

            if ('sma' in this.options.data_format_codes) this.get_sma()

            this.$forceUpdate()
        })

        Event.listen('prescriptions-loaded', (data) => {
            if (!data || !this.options.report) return

            this.data.prescriptions = this.data.prescriptions.concat(data)

            let need_other_medicine_stats = 'count' in this.options.report_status_codes && this.options.report_status_codes.count.includes('other_doctor_prescribed_medicine')
            let need_added_medicine_stats = 'count' in this.options.report_status_codes && this.options.report_status_codes.count.includes('added_medicine')


            if (need_other_medicine_stats) {
                let medicines = this.data.prescriptions.filter((m) => m.category_code == 'prescribed_medicine' && m.contract_id != this.contract_id)
                this.stats.count.other_doctor_prescribed_medicine = {value: medicines.length}
            }
            if (need_added_medicine_stats) {
                let medicines = this.data.prescriptions.filter((m) => m.category_code == 'added_medicine')
                this.stats.count.added_medicine = {value: medicines.length}
            }

            this.options.loaded = true
            this.$forceUpdate()
            Event.fire('refresh-report-status')
        })


        Event.listen('compliance-loaded', (data) => {
            if (!data || !this.options.report) return

            this.stats.compliance = this.stats.compliance.concat(data)

            let need_min_compliance_stats = 'min_compliance' in this.options.report_status_codes
            if (need_min_compliance_stats) {
                this.stats.min_compliance = {}
                this.options.report_status_codes.min_compliance.forEach((c) => {
                    let values = this.stats.compliance.filter((r) => r.category_code == c).map((r) => r.requested ? (r.done / r.requested ): 1)
                    this.stats.min_compliance[c] = {value: Math.min(...values) * 100}
                })
            }

            this.options.loaded = true
            this.$forceUpdate()
            Event.fire('refresh-report-status')
        })

        Event.listen('load-formalized-report', (report) => {
            this.options.report = report

            this.options.dates = [
                this.start_of_day(this.add_days(this.last_date, -6)),
                this.last_date
            ]

            if (window.PARAMS && window.PARAMS.date_from && window.PARAMS.date_to) {
                this.options.dates = [
                    new Date(window.PARAMS.date_from),
                    new Date(window.PARAMS.date_to)
                ]
            }

            this.load_data_format_codes()
            if (this.options.report.options.statuses != undefined) this.load_report_status_codes()

            this.load()
        })

        Event.listen('formalized-report-update-dates', (dates) => {
            this.options.dates = dates
            this.options.period = this.dates_difference(this.options.dates[0], this.options.dates[1])
            this.load()
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