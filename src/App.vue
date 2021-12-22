<template>
  <div style="padding-bottom: 15px;">
    <loading v-if="!patient"/>
    <load-error v-else-if="state == 'load-error'"></load-error>
    <div v-else>
      <dashboard-header :patient="patient"/>

      <div v-if="mode == 'settings' || mode == 'graph' || mode == 'report'">
        <div class="container" style="margin-top: 15px;">
          <dashboard :patient="patient" :categories="category_list" :mode="mode"
                     v-show="state == 'dashboard' || state == 'graph-category-chooser'"/>
          <report :patient="patient" :categories="category_list" :data="data" v-show="state == 'report'"/>
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

export default {
  name: 'App',
  components: {
    GraphPresenter,
    LoadError,
    Dashboard,
    Report,
    Loading,
    DashboardHeader,
  },
  data() {
    return {
      mode: undefined,
      state: "loading",
      patient: undefined,
      data: undefined,
    }
  },
  methods: {
    load: function () {
      this.axios.get(this.url('/api/settings/get_patient')).then(response => {
            this.patient = response.data
            this.axios.get(this.url('/api/categories')).then(this.process_load_answer);
          }
      );
    },
    process_load_answer: function (response) {
      this.category_list = response.data;

      if (this.mode == 'settings') {
        this.state = 'dashboard';
      }

      if (this.mode == 'graph') {
        this.state = 'graph-category-chooser'
      }

      if (this.mode == 'report') {
        Event.fire('load-report')
      }
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
          pages: response.data.page_cnt
        }

        this.state = 'report'
      });
    },
  },
  created() {
    this.mode = window.MODE

    console.log("running created");
    this.load();

    Event.listen('back-to-dashboard', () => this.state = 'dashboard');

    Event.listen('load-records', (data) => {
      this.load_records(data)
    })

    Event.listen('load-report', () => {
      let data = {
        dates: [undefined, undefined],
        page: 0,
        category: undefined
      }

      this.load_records(data)
      this.state = 'report'
    })

    Event.listen('load-graph', (params) => {
      this.state = 'graph'
    });
    Event.listen('load-heatmap', (params) => {
      this.state = 'graph'
    });

  },
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

h1, h2 {
  font-weight: normal;
}

a {
  color: #42b983;
}

body {
  background-color: #f8f8fb;
}
</style>
