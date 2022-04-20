<template>
  <div>
    <filter-panel page="report" :categories="filters"
                  :disable_downloading="!data || !data.records || !data.records.length"/>
    <loading v-if="!data"/>
    <div v-else>
      <!-- Ошибки -->
      <error-block :errors="errors" v-if="errors.length"></error-block>

      <!-- Записи -->
      <records-list :data="data.records"/>

      <!-- Список страниц -->
      <div class="row" v-if="data.pages">
        <button class="btn btn-link btn-sm" @click="select_page(page - 1)" v-if="page > 0">&#8592;
        </button>
        <a class="btn btn-link btn-sm" @click="select_page(p)" v-for="(o, p) in new Array(data.pages)"
           :style="p == data.page ? 'font-weight: bold; text-decoration: underline; color: black;' : ''">{{ p + 1 }}</a>
        <button class="btn btn-link btn-sm" @click="select_page(page + 1)" v-if="page < data.pages - 1">
          &#8594;
        </button>
      </div>

      <!-- Для экспорта -->
      <div v-show="false" v-if="data">
        <div ref="to-export" class="to-export">
          <h4>{{ data.report.title }}</h4>
          <br>
          <h6>Пациент: {{ patient.name }} ({{ patient.birthday }})</h6>
          <hr>
          <records-list :data="data.records" :to_export="true"/>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import RecordsList from "./parts/RecordsList";
import FilterPanel from "./parts/FilterPanel";
import html2pdf from "html2pdf.js";
import Loading from "./parts/Loading";
import ErrorBlock from "./parts/ErrorBlock";

export default {
  name: "Report",
  components: {Loading, FilterPanel, ErrorBlock, RecordsList},
  props: {
    patient: {
      required: true
    },
    categories: {
      required: true
    },
    data: {
      required: true
    }
  },
  data() {
    return {
      page: undefined,
      dates: undefined,
      filters: undefined,
      selected_categories: [],
      errors: []
    }
  },
  methods: {
    load: function () {
      this.errors = []
      let data = {
        dates: this.dates.map(date => date ? date.getTime() / 1000 : date),
        page: this.page,
        categories: this.selected_categories.length ? this.selected_categories.map(c => c.name) : this.data.report.categories,
        report: this.data.report
      }

      Event.fire('load-records', data)
    },
    select_page: function (p) {
      this.page = p
      this.load()
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
    }
  },
  created() {
    this.page = 0
    this.dates = [undefined, undefined]

    Event.listen('report-update-dates', (dates) => {
      this.page = 0
      this.dates = dates
      this.load()
    })

    Event.listen('update-categories', (categories) => {
      this.page = 0
      this.selected_categories = categories
      this.load()
    })

    Event.listen('generate-report', () => {
      this.generate_report()
    })

    Event.listen('incorrect-dates', (duration) => {
      this.errors = ['Выбран некорректный период']
    })

    Event.listen('load-report', (report) => {
      this.filters = report.filters
    })
  },
}
</script>

<style>
.to-export {
  font-size: smaller;
}

a {

}
</style>