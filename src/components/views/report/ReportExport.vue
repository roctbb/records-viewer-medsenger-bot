<template>
    <div ref="to-export">
        <h5>Отчет по мониторингу пациента {{ patient.name }} ({{ patient.birthday }})</h5>
        <span>
            <b>Период: </b>{{
                dates && dates[0] ? ` с ${dates[0].toLocaleDateString()}` : ''
            }} {{ dates && dates[1] ? ` по ${dates[1].toLocaleDateString()}` : '' }}
        </span>
        <hr>
        <h6>{{ options.report.title }}</h6>

        <!-- Таблица -->
        <records-table :to_export="true"/>

    </div>
</template>

<script>
import html2pdf from "html2pdf.js";
import RecordsTable from "./parts/RecordsTable.vue";

export default {
    name: "ReportExport",
    components: {RecordsTable},
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
                report: {},
            },
        }
    },
    methods: {
        reset_view: function () {
            this.flags.exporting = false
        },

        generate_report: function () {
            let element = this.$refs['to-export']

            let opt = {
                margin: 0.5,
                filename: this.patient.name + '.pdf',
                page_break: {mode: 'css'},
                html2canvas: {dpi: 192, letterRendering: true},
                jsPDF: {unit: 'in', format: 'a4', orientation: 'portrait'}
            };

            html2pdf().set(opt).from(element).save();
        }
    },
    created() {
        console.log('report-export created')

        // Страница с отчетом открыта
        Event.listen('load-report', (report) => {
            this.options.report = report
            this.$forceUpdate()
        })

        // Загрузка файла
        Event.listen('generate-report', () => {
            if (this.options.report.title) this.generate_report()
        });

        Event.listen('back-to-dashboard', () => this.options.report = {});
    },
}
</script>

<style>
.to-export {
    font-size: smaller;
}
</style>