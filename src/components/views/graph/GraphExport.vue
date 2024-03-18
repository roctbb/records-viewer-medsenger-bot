<template>
    <div ref="to-export">
        <h5>Отчет по мониторингу пациента {{ patient.name }} ({{ patient.birthday }})</h5>
        <span>
            <b>Период: </b>{{
                dates && dates[0] ? ` с ${dates[0].toLocaleDateString()}` : ''
            }} {{ dates && dates[1] ? ` по ${dates[1].toLocaleDateString()}` : '' }}
        </span>
        <hr>
        <h6>{{ options.graph.title }}</h6>

        <!-- График -->
        <line-graph :data='data' :dates="dates" :graph="options.graph" :to_export="true"
                    v-show="options.graph.type == 'line-graph'"/>
        <heatmap :data='data' :dates="dates" :graph="options.graph" :to_export="true"
                 v-show="options.graph.type == 'heatmap'"/>
        <day-line-graph :data='data' :dates="options.dates" :graph="options.graph" :to_export="true"
                    v-show="options.graph.type == 'day-graph'"/>

        <!-- Статистика -->
        <stats-table :data="data" :graph="options.graph"
                     v-show="['line-graph', 'day-graph'].includes(options.graph.type)"/>

        <!-- Табличка с симптомами -->
        <div class="center" v-if="list_data.length">
            <h5 class="text-center">Симптомы и события</h5>
            <records-table :data="list_data"/>
        </div>
    </div>
</template>

<script>
import LineGraph from "./graph-types/LineGraph.vue";
import Heatmap from "./graph-types/Heatmap.vue";
import StatsTable from "./parts/StatsTable.vue";
import RecordsList from "../report/parts/RecordsList.vue";
import html2pdf from "html2pdf.js";
import DayLineGraph from "./graph-types/DayLineGraph.vue";
import RecordsTable from "../report/parts/RecordsTable.vue";

export default {
    name: "GraphExport",
    components: {RecordsTable, DayLineGraph, Heatmap, RecordsList, StatsTable, LineGraph},
    props: {
        patient: {required: true},
        dates: {required: true},
        data: {required: true}
    },
    data() {
        return {
            flags: {
                exporting: false
            },
            options: {
                graph: {},
                text_categories: ['symptom', 'medicine', 'patient_comment', 'information', 'side_effect'],
                dates: [new Date(), new Date()]
            }
        }
    },
    computed: {
        list_data() {
            if (!this.data.all) return []

            return this.data.all.filter(record =>
                this.options.text_categories.includes(record.category_info.name))
        }
    },
    methods: {
        reset_view: function () {
            this.flags.exporting = false
        },
        generate_report: function () {
            this.options.exporting = true

            let element = this.$refs['to-export']

            let opt = {
                margin: 0.5,
                filename: `${this.options.graph.title}_${this.patient.name}.pdf`,
                page_break: {mode: 'css'},
                html2canvas: {dpi: 192, letterRendering: true},
                jsPDF: {unit: 'in', format: 'a4', orientation: 'portrait'}
            };
            setTimeout(() => {
                this.flags.exporting = false;
            }, 5000);
            html2pdf().set(opt).from(element).save();
        },

    },
    created() {
        console.log('graph-export created')

        // Страница с графиком открыта
        Event.listen('load-graph-view', (params) => {
            this.options.graph = params
            this.$forceUpdate()
        });

        // Загрузка файла
        Event.listen('generate-report', () => {
            if (this.options.graph.title) this.generate_report()
        });

        Event.listen('back-to-dashboard', () => this.options.graph = {});
    }
}

</script>

<style>
</style>