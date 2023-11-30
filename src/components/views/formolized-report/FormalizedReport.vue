<template>
    <div v-if="options.report">
        <h4>{{ options.report.title }}</h4>
        <filter-panel page="formalized-report" :patient="patient"
                      :disable_downloading="!data.records || !data.records.length" :last_date="last_date"/>

        <loading v-if="!options.loaded"/>

        <div v-else>
            <!-- Ошибки -->
            <error-block :errors="errors" v-if="errors.length"/>

            <!-- Описание -->
            <div style="margin-top: 15px;" class="alert alert-info" role="alert"
                 v-if="options.report.options.description">
                <span v-html="options.report.options.description"/>
            </div>

            <!-- Блоки -->
            <report-block :block="block" :data="block_data"
                          :key="'block-' + i"
                          v-for="(block, i) in options.report.options.blocks"/>

            <!-- Для экспорта -->
            <div v-show="false" v-if="options.loaded">
                <div ref="to-export" class="to-export">
                    <h4>{{ options.report.title }}</h4>
                    <br>
                    <h6>Пациент: {{ patient.name }} ({{ patient.birthday }})</h6>
                    <span><b>Период: </b>{{
                            options.dates[0] ? ` с ${options.dates[0].toLocaleDateString()}` : ''
                        }} {{ options.dates[1] ? ` по ${options.dates[1].toLocaleDateString()}` : '' }}</span>
                    <hr>

                    <hr>
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

export default {
    name: "FormalizedReport",
    components: {ReportBlock, Loading, FilterPanel, ErrorBlock},
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
                period: undefined,
                data_format_codes: undefined
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
                type: 'formalized-report'
            }
        }
    },
    methods: {
        load: function () {
            this.options.loaded = false
            this.errors = []

            let categories = this.options.report.categories
            let dates = this.options.dates.map(date => date ? date.getTime() / 1000 : date)
            let options = {
                type: 'formalized-report'
            }

            this.load_data(categories, dates, options)
        },
        load_data_format_codes: function () {
            let codes = {}

            // this.stats = {}
            this.stats.zones = {}

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

                        if (part.code.includes('zone')) {
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
            records.forEach(record => {
                if (this.options.data_format_codes.algorithm_comments.includes(record.category_code)) {
                    let comment_additions = this.comment_additions(record)
                    record.comments = comment_additions.map((a) => a['addition']['comment'])
                }
            })
        },

        generate_report: function () {
            let element = this.$refs['to-export']

            let opt = {
                margin: 0.5,
                filename: this.patient.name + '.pdf',
                page_break: {mode: 'css'},
                // image:        { type: 'jpeg', quality: 0.98 },
                html2canvas: {dpi: 192, letterRendering: true},
                jsPDF: {unit: 'in', format: 'letter', orientation: 'portrait'}
            };

            html2pdf().set(opt).from(element).save();
        },

        // values
        get_sma: function () {
            this.stats.sma = {}
            this.options.data_format_codes.sma.forEach((category) => {
                this.stats.sma[category] = this.simple_moving_average(
                    this.data.records_by_categories_by_dates[category],
                    this.data.additional_records[category],
                    this.options.period, this.format_date(this.options.dates[1])
                )
            })

            /* sma structure
            * "category" : {
            *     value: ..,
            *     credible: ..,
            *     filled_days: ..
            * }
            */

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
        },

    },
    mounted() {
        this.options.dates = [undefined, this.last_date]
    },
    created() {
        Event.listen('loaded', (data) => {
            if (data.info.type != 'formalized-report') return

            this.stats.sma = {}
            this.stats.compliance = []

            if ('zone_cnt' in this.options.data_format_codes ||
                'zone_percent' in this.options.data_format_codes) this.add_zones(data.records)

            if ('algorithm_comments' in this.options.data_format_codes) this.add_comments(data.records)

            this.data.records = data.records
            this.data.records_by_categories = this.group_by(data.records, 'category_code')
            this.data.records_by_categories_by_dates = this.group_records_by_categories_by_dates(this.data.records_by_categories, true)
            this.data.record_groups = this.get_record_groups(data.records, true)
            this.data.prescriptions = []

            Event.fire('set-dates', this.options.dates)
            this.options.period = this.dates_difference(this.options.dates[0], this.options.dates[1])

            if ('zone_cnt' in this.options.data_format_codes ||
                'zone_percent' in this.options.data_format_codes) this.get_zones_distribution()

            this.options.loaded = true

            if ('sma' in this.options.data_format_codes)
                this.load_additional_data(this.options.data_format_codes.sma, this.options.dates[0].getTime(),
                    1, 'formalized-report')

            if ('medicine_description' in this.options.data_format_codes) {
                this.options.loaded = false

                this.send_order('get_medicines', window.AGENTS.FORMS_AGENT_ID, {
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

            this.options.loaded = true
            this.$forceUpdate()
        })


        Event.listen('compliance-loaded', (data) => {
            if (!data || !this.options.report) return

            this.stats.compliance = this.stats.compliance.concat(data)

            this.options.loaded = true
            this.$forceUpdate()
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
            this.load()
        })

        Event.listen('formalized-report-update-dates', (dates) => {
            this.options.dates = dates
            this.options.period = this.dates_difference(this.options.dates[0], this.options.dates[1])
            this.load()
        })


        Event.listen('generate-formalized-report', () => {
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