<template>
  <div style="padding-bottom: 15px;">
    <loading v-if="!loaded"/>
    <load-error v-else-if="state == 'load-error'"/>
    <action-done v-else-if="state == 'done'"/>
    <div v-else>
      <dashboard-header :patient="patient"/>

      <div
          v-if="window_mode == 'settings' || window_mode == 'graph' || window_mode == 'log' || window_mode == 'conclusion'">
        <div class="container slim-container" style="margin-top: 15px;">
          <dashboard :patient="patient" :categories="category_list"
                     v-show="state == 'dashboard' || state == 'graph-category-chooser'"/>
          <report :patient="patient" :categories="category_list" :data="data" v-show="state == 'report'"/>
          <conclusion-editor :patient="patient" v-show="state == 'conclusion'"/>
        </div>
        <graph-presenter :patient="patient" v-show="state == 'graph'"/>
      </div>

    </div>
  </div>
</template>

<script>
import DashboardHeader from "./components/parts/DashboardHeader";
import Loading from "./components/parts/Loading";
import Report from "./components/Report";
import Dashboard from "./components/Dashboard";
import LoadError from "./components/LoadError";
import GraphPresenter from "./components/GraphPresenter";
import * as moment from "moment/moment";
import ConclusionEditor from "./components/ConclusionEditor";
import ActionDone from "./components/ActionDone";

export default {
  name: 'App',
  components: {
    ActionDone,
    ConclusionEditor,
    GraphPresenter,
    LoadError,
    Dashboard,
    Report,
    Loading,
    DashboardHeader,
  },
  data() {
    return {
      state: "loading",
      patient: undefined,
      data: undefined,
      loaded: false
    }
  },
  methods: {
    load: function () {
      this.loaded = false
      this.axios.get(this.url('/api/settings/get_patient')).then(response => {
            this.patient = response.data
            this.axios.get(this.url('/api/categories')).then(this.process_load_answer);
          }
      );
    },
    process_load_answer: function (response) {
      this.category_list = response.data;

      if (this.window_mode == 'settings') {
        this.state = 'dashboard';
      }

      if (this.window_mode == 'conclusion') {
        this.state = 'conclusion';
      }

      if (this.window_mode == 'graph') {
        this.state = 'graph-category-chooser'
      }

      if (this.window_mode == 'log') {
        this.state = 'log'
        let params = {
          title: 'История назначений',
          categories: ['doctor_action'],
          filters: undefined
        }
        Event.fire('load-report', params)
      }
      this.loaded = true
    },
    process_load_error: function (response) {
      this.state = 'load-error'
    },

    load_records: function (data) {
      this.data = null

      this.axios.post(this.url('/api/report'), data).then(response => {
        this.data = {
          records: response.data.dates,
          page: data.page,
          pages: response.data.page_cnt,
          report: data.report
        }

        this.state = 'report'
      });
    },
  },
  created() {
    this.window_mode = window.MODE

    console.log("running created");
    this.load();

    Event.listen('back-to-dashboard', () => this.state = 'dashboard');
    Event.listen('load-error', () => this.state = 'load-error')
    Event.listen('action-done', () => this.state = 'done')

    Event.listen('load-records', (data) => {
      this.load_records(data)
    })

    Event.listen('load-report', (report) => {
      this.loaded = false
      let end_date = new Date(moment(this.patient.end_date).set({
        hour: 23,
        minute: 59,
        second: 59
      }).format('YYYY-MM-DD HH:mm:ss'))
      let today = new Date(moment().set({
        hour: 23,
        minute: 59,
        second: 59
      }).format('YYYY-MM-DD HH:mm:ss'))
      let end_filter_date = end_date < today ? end_date : today

      let data = {
        dates: [undefined, +end_filter_date / 1000],
        page: 0,
        categories: report.categories,
        report: report
      }

      this.load_records(data)
      this.state = 'report'
      this.loaded = true
    })

    Event.listen('load-graph', (params) => {
      this.state = 'graph'
    });
    Event.listen('load-day-graph', (params) => {
      this.state = 'graph'
    });
    Event.listen('load-heatmap', (params) => {
      this.state = 'graph'
    });

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

</style>