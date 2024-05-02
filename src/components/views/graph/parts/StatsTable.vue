<template>
    <div>
        <h5 class="text-center">Статистика показателей за выбранный период</h5>
        <loading v-if="!flags.ready"/>
        <div v-else>
            <!-- Веб -->
            <table class="table table-hover text-center" v-if="!mobile">
                <colgroup>
                    <col span="1" style="width: 55%;">
                    <col span="1" style="width: 15%;">
                    <col span="1" style="width: 15%;">
                    <col span="1" style="width: 15%;">
                </colgroup>

                <thead>
                <tr>
                    <th scope="col">Показатель</th>
                    <th scope="col">Среднее</th>
                    <th scope="col">Мин</th>
                    <th scope="col">Макс</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="stat in statistics">
                    <td style="text-align: left;"><b>{{ stat.name }}</b></td>
                    <td>{{ stat.avg.toFixed(2) * 1 }}</td>
                    <td>{{ stat.min.toFixed(2) * 1 }}</td>
                    <td>{{ stat.max.toFixed(2) * 1 }}</td>
                </tr>
                </tbody>
            </table>

            <!-- Мобилка -->
            <div v-else v-for="(stat, index) in statistics">
                <h6>{{ stat.name }}</h6>
                <table class="table table-hover table-sm text-center">
                    <colgroup>
                        <col span="1" style="width: 34%;">
                        <col span="1" style="width: 33%;">
                        <col span="1" style="width: 33%;">
                    </colgroup>
                    <thead>
                    <tr>
                        <th scope="col">Среднее</th>
                        <th scope="col">Мин</th>
                        <th scope="col">Макс</th>
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
    </div>
</template>

<script>
import Loading from "../../../common/Loading.vue";
import getPulsePressureStats from "../../../../scripts/StatsScript_PulsePressure";


export default {
    name: "StatsTable",
    components: {Loading},
    props: {
        data: {required: true},
        graph: {required: true}
    },
    data() {
        return {
            flags: {
                ready: false,
            },
            options: {
                text_categories: ['symptom', 'medicine', 'patient_comment', 'information', 'side_effect']
            },
            statistics: [],
            records: {
                all: undefined,
                by_categories: undefined,
                additional: undefined
            }
        }
    },
    computed: {},
    methods: {
        reset_view: function () {
            this.flags.ready = false
        },

        refresh_stats: function (start, end) {
            this.flags.ready = false
            let stats = []

            Object.entries(this.records.by_categories).forEach(([category, records]) => {
                if (!this.options.text_categories.includes(category)) {
                    let visible_values = this.find_visible_records(records, start, end)

                    if (visible_values.length) {
                        // calculate statistics for visible points
                        const max = visible_values.reduce((a, b) => Math.max(a, b))
                        const min = visible_values.reduce((a, b) => Math.min(a, b))
                        let average = visible_values.reduce((a, b) => a + b, 0) / visible_values.length

                        if (records[0].category_type == 'integer') {
                            average = Math.ceil(average)
                        }

                        stats.push({
                            name: records[0].category_info.description,
                            code: records[0].category_info.name,
                            data: visible_values,
                            avg: average,
                            min: min,
                            max: max
                        })

                    }
                }
            })


            // Дополнительные показатели
            let additional
            switch (this.graph.options.additional_stats_script) {
                case "pulse_pressure":
                    additional = getPulsePressureStats(stats)
                    break
                default:
                    additional = []
                    break
            }
            stats = stats.concat(additional)

            this.statistics = stats
            this.flags.ready = true
        },

        find_visible_records: function (records, start, end) {
            let timestamps = records.map(record => record.timestamp * 1000)

            let start_index = this.binary_search(timestamps, start, 0, timestamps.length - 1)
            let end_index = this.binary_search(timestamps, end, 0, timestamps.length - 1)

            return records.slice(start_index, end_index).map(record => record.value)
        },
    },
    mounted() {
        // Первая отрисовка графика
        Event.listen('draw-graph', (options_getter) => {
            this.reset_view()

            this.records.all = this.data.all
            this.records.by_categories = this.data.by_categories
        })

        Event.listen('refresh-stats', (data) => {
            this.refresh_stats(data.start, data.end)
        });

    }

}
</script>


<style scoped>
</style>