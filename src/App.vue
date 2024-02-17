<template>
    <div style="padding-bottom: 15px;">
        <vue-confirm-dialog/>
        <loading v-if="!loaded"/>
        <load-error v-else-if="state == 'load-error'"/>
        <action-done v-else-if="state == 'done'"/>
        <div v-else>
            <div>
                <div class="container slim-container" style="margin-top: 15px;">
                    <dashboard :patient="patient" v-show="state == 'dashboard' || state == 'graph-category-chooser'"/>
                    <report :patient="patient" :last_date="last_date" v-show="state == 'report'"/>
                    <formalized-report :params="params" :patient="patient" :last_date="last_date" v-show="state == 'formalized-report'"/>
                    <graph-presenter :patient="patient" :last_date="last_date" v-show="state == 'graph'"/>
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
import GraphPresenter from "./components/views/graph/GraphPresenter.vue";
import ConclusionEditor from "./components/views/conclusion/ConclusionEditor.vue";
import ActionDone from "./components/common/ActionDone.vue";
import FormalizedReport from "./components/views/formalized-report/FormalizedReport.vue";

export default {
    name: 'App',
    components: {
        ActionDone, Loading, LoadError,
        GraphPresenter, Report, FormalizedReport,
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

            this.send_order('get_params', window.AGENTS.FORMS_AGENT_ID, {}, 'params-loaded')
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
            this.state = 'load-error'
        },
    },
    created() {
        console.log("running created");
        this.load();

        Event.listen('back-to-dashboard', () => this.state = 'dashboard');
        Event.listen('load-error', () => this.state = 'load-error')
        Event.listen('action-done', () => this.state = 'done')

        Event.listen('load-report', (report) => {
            this.state = 'report'
        })

        Event.listen('load-formalized-report', (report) => {
            this.state = 'formalized-report'
        })

        Event.listen('load-line-graph', (params) => {
            this.state = 'graph'
        });
        Event.listen('load-day-graph', (params) => {
            this.state = 'graph'
        });
        Event.listen('load-heatmap', (params) => {
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
</style>