<template>
  <div v-if="patient && categories && !object_id">
    <div v-if="window_mode != 'graph'">
      <h5>Отчеты</h5>
      <div class="row">
        <card v-for="(report, i) in report_categories" :key="'report_' + i" :image="images.report"
              class="col-lg-3 col-md-4">
          <h6>{{ report.title }}</h6>
          <a @click="load_report(report)" href="#" class="btn btn-primary">Открыть</a>
        </card>
      </div>
    </div>

    <div v-if="plottable_categories.length">
      <h5>Графики</h5>
      <div class="row">
        <card v-for="(category, i) in plottable_categories" :key="'graph_' + i" :image="images.graph"
              class="col-lg-3 col-md-4">
          <h6>{{ category.title }}</h6>

          <a @click="load_graph(category, 'graph')" href="#" class="btn btn-primary">Открыть</a>
        </card>
      </div>
    </div>

    <div v-if="plottable_day_graphs.length">
      <h5>Графики по суткам</h5>
      <div class="row">
        <card v-for="(category, i) in plottable_day_graphs" :key="'day_graph_' + i" :image="images.graph"
              class="col-lg-3 col-md-4">
          <h6>{{ category.title }} (сутки)</h6>
          <a @click="load_graph(category, 'day-graph')" href="#" class="btn btn-primary">Открыть</a>
        </card>
      </div>
    </div>

    <div v-if="plottable_heatmap_categories.length">
      <h5>Тепловые карты</h5>
      <div class="row">
        <card v-for="(category, i) in plottable_heatmap_categories" :key="'heatmap_' + i" :image="images.heatmap"
              class="col-lg-3 col-md-4">
          <h6>{{ category.title }}</h6>
          <a @click="load_graph(category, 'heatmap')" href="#" class="btn btn-primary">Открыть</a>
        </card>
      </div>
    </div>

    <div style="margin-top: 15px;" class="alert alert-info" role="alert">
      <p>В этом разделе можно посмотреть внесенные данные разных представлениях:</p>
      <ul>
        <li v-if="window_mode == 'settings'"><strong>В виде отчета</strong>. Таблица записей фильтруются по датам и
          категориям.
          Отчет доступен для скачивания в формате PDF.
        </li>
        <li><strong>В виде графиков.</strong> Числовые данные отображаются в виде кривых, а текстовые (симптомы,
          лекарства и комментарии) на линии в нижней части графика. Чтобы посмотреть подробную информацию, наведите
          мышку на нужную точку графика.
        </li>
        <li><strong>В виде суточных графиков.</strong> Числовые данные отображаются в виде кривых, а текстовые
          (симптомы, лекарства и комментарии) – при наведении на нужную точку графика.
        </li>
        <li><strong>В виде тепловых карт.</strong> Симптомы и приемы лекарств отображаются с частотой появления за
          день. Чтобы посмотреть подробную информацию, наведите мышку на нужную ячейку карты.
        </li>
      </ul>
    </div>

  </div>
</template>

<script>
import Card from "./parts/Card";
import * as moment from "moment/moment";

export default {
  name: "Dashboard",
  components: {Card},
  props: {
    patient: {
      required: true
    },
    categories: {
      required: true
    }
  },
  data() {
    return {
      custom_reports: [
        {
          title: 'Отчет по мониторингу',
          categories: [],
          filters: []
        },
        {
          title: 'История назначений',
          categories: ['doctor_action'],
          filters: undefined
        },
      ],
      groups: [
        {
          title: "Давление и пульс",
          categories: ['systolic_pressure', 'diastolic_pressure', 'pulse'],
        },
        {
          title: "Обхват голеней",
          categories: ['leg_circumference_right', 'leg_circumference_left'],
        },
        {
          title: "Глюкоза",
          categories: ['glukose', 'glukose_fasting', 'glukose_food'],
        }
      ],
      heatmaps: [
        {
          title: "Симптомы",
          categories: ['symptom', 'medicine'],
        },
        {
          title: "Приемы лекарств",
          categories: ['medicine'],
        },
      ],
      day_graphs: [
        {
          title: "Глюкоза",
          categories: ['glukose', 'glukose_fasting', 'glukose_food']
        }
      ]
    }
  },
  computed: {
    plottable_categories: function () {
      let plottable = this.categories.filter((category) => {
        return !category.is_legacy && ['scatter', 'values'].includes(category.default_representation) &&
            !['string', 'file'].includes(category.type)
      })

      let custom = this.groups.filter((group) => {
        return group.categories.some((category_name) => {
          return plottable.filter((category) => category.name == category_name).length > 0
        })
      })

      let not_custom = plottable.filter((category) => {
        return !this.groups.some((group) => {
          return group.categories.includes(category.name)
        })
      })

      not_custom.forEach((category) => {
        custom.push({
          title: category.description,
          categories: [category.name]
        })
      })

      return custom
    },
    plottable_heatmap_categories: function () {
      return this.heatmaps.filter(heatmap => !heatmap.categories.filter(c => !this.categories.map(cc => cc.name).includes(c)).length)
    },
    plottable_day_graphs: function () {
      return this.day_graphs.filter(graph => graph.categories.filter(c => !this.categories.map(cc => cc.name).includes(c)).length != graph.categories.length)
    },
    report_categories: function () {
      this.custom_reports[0].categories = this.categories.map(c => c.name).filter(c => c != 'doctor_action')
      this.custom_reports[0].filters = this.categories.filter(c => c.name != 'doctor_action')

      // Добавляет в отчеты категории с файлами
      /*
      let categories = this.categories.filter((category) => {
        return category.type == 'file'
      })

      let custom = this.custom_reports
      categories.forEach((category) => {
        custom.push({
          title: category.description,
          categories: [category.name],
          filters: undefined
        })
      })
      */

      let custom = this.custom_reports

      if (this.source == 'patient') {
        custom = custom.filter(c => c.title != 'История назначений')
      }

      return custom
    }
  },
  methods: {
    load_report: function (params) {
      Event.fire('load-report', params)
    },
    load_graph: function (params, type) {
      let end_date = new Date(this.patient.end_date)
      let today = new Date(moment().format('YYYY-MM-DD'))
      let end_filter_date = end_date < today ? end_date : today

      let data = {
        group: params,
        dates: [new Date(moment(end_filter_date).add(-14, 'days').format('YYYY-MM-DD')), end_filter_date],
        onload: type != 'day-graph'
      }

      Event.fire('load-' + type, data)
    },
  },
  mounted() {
    Event.listen('back-to-dashboard', () => {
      // понятия не имею, почему оно изменяется
      this.day_graphs = [
        {
          title: "Глюкоза",
          categories: ['glukose', 'glukose_fasting', 'glukose_food']
        }
      ]
    })

    if (this.object_id) {
      let end_date = new Date(this.patient.end_date)
      let today = new Date(moment().format('YYYY-MM-DD'))
      let end_filter_date = end_date < today ? end_date : today

      this.axios.get(this.url('/api/categories')).then(response => {
        try {
          let category = response.data.filter(c => c.id == this.object_id)
          if (category.length) {
            let name = category[0].name;
            let params = this.plottable_categories.filter(c => c.categories.includes(name))[0];
            let data = {
              group: params,
              dates: [new Date(moment(end_filter_date).add(-14, 'days').format('YYYY-MM-DD')), end_filter_date]
            }

            Event.fire('load-graph', data);
          }
        } catch (e) {
          console.log(e);
        }
      });
    }
  }
}
</script>

<style scoped>

</style>