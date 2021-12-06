<template>
  <div style="padding-bottom: 15px;">
    <loading v-if="!patient"/>
    <div style="padding-bottom: 5px;" v-else>
      <dashboard-header :patient="patient"/>
      <div class="container">
        <h3>Отчет по мониторингу пациента</h3>
        <filter-panel/>
        <button class="btn btn-sm btn-primary" v-if="!mobile" :disabled="state != 'loaded'"
                @click="generateReport()">Скачать PDF</button>
        <hr>

        <loading v-if="state == 'loading'"/>
        <div v-else>
          <records-list :data="records"/>

          <div class="row" v-if="page_cnt">
            <button class="btn btn-link btn-sm" @click="select_page(selected_page - 1)" v-if="selected_page > 0">&#8592;
            </button>
            <a class="btn btn-link btn-sm" @click="select_page(p)" v-for="(o, p) in new Array(page_cnt)"
               :style="p == selected_page ? 'font-weight: bold; text-decoration: underline; color: black;' : ''">{{ p + 1 }}</a>
            <button class="btn btn-link btn-sm" @click="select_page(selected_page + 1)" v-if="selected_page < page_cnt - 1">
              &#8594;
            </button>
          </div>
        </div>
      </div>

      <div v-show="false">
        <div ref="to-export" class="to-export">
          <h3>Отчет по мониторингу пациента {{ patient.name }} ({{ patient.birthday }})</h3>
          <hr>
          <records-list :data="records" :to_export="true"/>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import html2pdf from 'html2pdf.js'
import DashboardHeader from "./components/parts/DashboardHeader";
import Loading from "./components/Loading";
import FilterPanel from "./components/parts/FilterPanel";
import RecordsList from "./components/parts/RecordsList";

export default {
  name: 'App',
  components: {
    FilterPanel,
    RecordsList,
    Loading,
    DashboardHeader,
  },
  data() {
    return {
      state: "loading",
      patient: undefined,
      records: undefined,
      page_cnt: undefined,
      selected_page: undefined,
      selected_category: undefined,
      selected_categories: undefined,
      selected_dates: undefined
    }
  },
  methods: {
    load: function () {
      this.axios.get(this.url('/api/settings/get_patient')).then((response) => {
        this.patient = response.data;
        this.selected_page = 0
        this.selected_dates = [undefined, undefined]
        this.selected_categories = []
        this.load_records()
      });
    },
    load_records: function () {
      this.state = 'loading'

      let data = {
        dates: this.selected_dates.map(date => date ? date.getTime() / 1000 : date),
        categories: this.selected_categories,
        page: this.selected_page,
        category: this.selected_category
      }

      this.axios.post(this.url('/api/report'), data).then(response => {
        this.records = response.data.dates

        if (response.data.page_cnt != null) {
          this.page_cnt = response.data.page_cnt
        }

        this.state = 'loaded'
      });
    },
    select_page: function (p) {
      this.selected_page = p
      this.load_records()
    },
    generateReport: function () {
      this.state = 'exporting'

      let element = this.$refs['to-export']
      console.log(element)
      let opt = {
        margin:       0.5,
        filename:     this.patient.name + '.pdf',
        page_break:   { mode: 'css' },
        // image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { dpi: 192, letterRendering: true },
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
      };

      html2pdf().set(opt).from(element).save();

      this.state = "loaded"
    }
  },
  created() {
    console.log("running created");
    this.load();

    Event.listen('update-dates', (dates) => {
      this.selected_page = 0
      this.selected_dates = dates
      this.load_records()
    })

    Event.listen('update-categories', (categories) => {
      this.selected_page = 0
      this.selected_categories = categories
      this.load_records()
    })

    Event.listen('update-category', (category) => {
      this.selected_page = 0
      this.selected_category = category
      this.load_records()
    })
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

.to-export {
  font-size: smaller;
}
</style>
