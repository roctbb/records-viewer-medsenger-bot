<template>
    <div style="padding-bottom: 15px;">
        <vue-confirm-dialog/>
        <load-error/>

        <loading v-if="!loaded"/>
        <action-done v-else-if="state == 'done'"/>
        <div v-else>
            <div>
                <div class="container slim-container" style="margin-top: 15px;">
                    <dashboard :patient="patient" v-show="state == 'dashboard' || state == 'graph-category-chooser'"/>
                    <report :patient="patient" :last_date="last_date" v-show="state == 'report'"/>
                    <formalized-report :params="params" :patient="patient" :last_date="last_date" v-show="state == 'formalized-report'"/>
                    <graph-view :patient="patient" :last_date="last_date" v-show="state == 'graph'"/>
                    <conclusion-editor :patient="patient" v-show="state == 'conclusion'"/>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import DashboardHeader from "./components/views/dashboard/DashboardHeader.vue";
import Loading from "./components/common/Loading.vue";
import Report from "./components/views/report/Report.vue";
import Dashboard from "./components/views/dashboard/Dashboard.vue";
import LoadError from "./components/common/LoadError.vue";
import ConclusionEditor from "./components/views/conclusion/ConclusionEditor.vue";
import ActionDone from "./components/common/ActionDone.vue";
import FormalizedReport from "./components/views/report/FormalizedReport.vue";
import GraphView from "./components/views/graph/GraphView.vue";

export default {
    name: 'App',
    components: {
        GraphView,
        ActionDone, Loading, LoadError,
        Report, FormalizedReport,
        Dashboard, DashboardHeader,
        ConclusionEditor
    },
    data() {
        return {
            state: "loading",
            patient: undefined,
            data: undefined,
            params: {},
            loaded: false
        }
    },
    computed: {
        last_date() {
            let today = this.end_of_day(new Date())
            if (!this.patient) return today

            let end_date = this.end_of_day(new Date(this.patient.end_date))
            return end_date < today ? end_date : today
        }
    },
    methods: {
        load: function () {
            this.loaded = false
            this.axios
                .get(this.direct_url('/api/get_patient'))
                .then(this.process_load_answer);

            this.send_order('get_params', 'FORMS', {}, 'params-loaded')
        },
        process_load_answer: function (response) {
            this.patient = response.data

            if (['settings', 'graph-presenter', 'group-presenter'].includes(this.window_mode)) {
                this.state = 'dashboard'
            }

            if (this.window_mode == 'conclusion') {
                this.state = 'conclusion'
            }

            if (this.window_mode == 'graph') {
                this.state = 'graph-category-chooser'
            }

            if (this.window_mode == 'log') {
                window.OBJECT_ID = 2
                this.state = 'dashboard'
            }
            this.loaded = true
        },
        process_load_error: function (response) {
            this.$modal.show('load-error', {})
        },
    },
    created() {
        console.log("running created");
        this.load();

        Event.listen('back-to-dashboard', () => this.state = 'dashboard');
        Event.listen('load-error', () => this.$modal.show('load-error', {})
        )
        Event.listen('action-done', () => this.state = 'done')

        Event.listen('load-report', (report) => {
            this.state = 'report'
        })

        Event.listen('load-formalized-report', (report) => {
            this.state = 'formalized-report'
        })

        Event.listen('load-graph-view', (params) => {
            this.state = 'graph'
        });


        Event.listen('params-loaded', (data) => {
            this.params = {}

            data.forEach((param) => {
                this.params[param.code] = {
                    name: param.name,
                    value: param.value
                }
            })

            this.$forceUpdate()
        })


    },
}
</script>

<style>
input[type=checkbox] {
    /* Double-sized Checkboxes */
    -ms-transform: scale(1.2); /* IE */
    -moz-transform: scale(1.2); /* FF */
    -webkit-transform: scale(1.2); /* Safari and Chrome */
    -o-transform: scale(1.2); /* Opera */
    transform: scale(1.2);
    margin: 10px;
}

.content-container {
    justify-content: center;
    align-items: center;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
}

.row {
    margin-left: 0;
    margin-right: 0;
    column-gap: 0;
}

table {
    border-collapse: collapse;
    border: 1px solid #fcfcfc;
    border-bottom: 3px solid #24a8b4;
}


table th {
    padding: 5px 10px !important;
}

table td {
    padding: 5px 10px !important;
    font-size: 14px;
}

table tr {
    break-inside: avoid;
}

table tr:hover {
    background: #f4f4f4;
}

table tr:hover td {
    color: #555;
}

table th, table td {
    border-collapse: collapse;
}

table th {
    background: #24a8b4;
    color: #fff;
}

img {
    object-fit: contain;
    object-position: left top;
}

.alert {
    margin-bottom: 5px;
}

.alert-danger-outline {
    color: #b60909;
    border-left: 3px solid #dc0909;
    border-radius: 0 5px 5px 0;
    padding: 5px 15px;
    background-color: #f5535333;
}

.alert-info-outline {
    color: #006c88;
    border-left: 3px solid #24a8b4;
    border-radius: 0 5px 5px 0;
    padding: 5px 15px;
    background-color: #72d6e033;
}

.alert-secondary-outline {
    border-left: 3px solid #4b4b4b;
    border-radius: 0 5px 5px 0;
    padding: 5px 15px;
    background-color: #7d7d7d80;
}
</style>