<template>
  <div>
    <filter-panel page="report" :categories="categories" :disable_downloading="!data || !data.records.length"/>
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
      <div v-show="false">
        <div ref="to-export" class="to-export">
          <h4>Отчет по мониторингу пациента {{ patient.name }} ({{ patient.birthday }})</h4>
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
      errors: []
    }
  },
  methods: {
    load: function (categories) {
      this.errors = []
      let data = {
        dates: this.dates.map(date => date ? date.getTime() / 1000 : date),
        page: this.page,
        categories: categories.length ? categories.map(c => c.name) : null
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
      this.load(categories)
    })

    Event.listen('generate-report', () => {
      this.generate_report()
    })

    Event.listen('incorrect-dates', () => {
      this.errors = ['Выбран некорректный период']
    })

  },
}
</script>

<style scoped>
.to-export {
  font-size: smaller;
}
</style>