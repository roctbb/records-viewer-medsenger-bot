<template>
  <div v-if="patient && categories">
    <div v-if="window_mode != 'graph'">
      <h5>Доступные отчеты</h5>
      <div class="row">
        <card key="main_report" :image="images.report" class="col-lg-3 col-md-4">
          <h6>Общий отчет по датам</h6>
          <a @click="load_report()" href="#" class="btn btn-primary">Открыть</a>
        </card>
      </div>

    </div>

    <div v-if="plottable_categories.length">
      <h5>Доступные графики</h5>
      <div class="row">
        <card v-for="(category, i) in plottable_categories" :key="'graph_' + i" :image="images.graph"
              class="col-lg-3 col-md-4">
          <h6>{{ category.title }}</h6>

          <a @click="load_graph(category)" href="#" class="btn btn-primary">Открыть</a>
        </card>
      </div>
    </div>

    <div v-if="heatmaps.length">
      <h5>Доступные тепловые карты</h5>
      <div class="row">
        <card v-for="(category, i) in heatmaps" :key="'heatmap_' + i" :image="images.heatmap" class="col-lg-3 col-md-4">
          <h6>{{ category.title }}</h6>
          <a @click="load_heatmap(category)" href="#" class="btn btn-primary">Открыть</a>
        </card>
      </div>

      <div style="margin-top: 15px;" class="alert alert-info" role="alert">
        <p>В этом разделе можно посмотреть внесенные данные разных представлениях:</p>
        <ul>
          <li v-if="window_mode == 'settings'"><strong>В виде отчета</strong>. Таблица записей фильтруются по датам и категориям.
            Отчет доступен для скачивания в формате PDF.
          </li>
          <li><strong>В виде графиков.</strong> Числовые данные отображаются в виде кривых, а текстовые (симптомы и лекарства) на
            линии в нижней
            части графика. Чтобы посмотреть подробную информацию, наведите мышку на нужную точку графика.
          </li>
          <li><strong>В виде тепловых карт.</strong> Симптомы и приемы лекарств отображаются с частотой появления за день.
            Чтобы посмотреть подробную информацию, наведите мышку на нужную ячейку карты.
          </li>
        </ul>
      </div>

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
      groups: [
        {
          "title": "Давление и пульс",
          "categories": ['systolic_pressure', 'diastolic_pressure', 'pulse'],
        },
        {
          "title": "Обхват голеней",
          "categories": ['leg_circumference_right', 'leg_circumference_left'],
        },
        {
          "title": "Глюкоза",
          "categories": ['glukose', 'glukose_fasting'],
        }
      ],
      heatmaps: [
        {
          "title": "Симптомы",
          "categories": ['symptom', 'medicine'],
        },
        {
          "title": "Приемы лекарств",
          "categories": ['medicine'],
        }
      ]
    }
  },
  computed: {
    plottable_categories: function () {
      let plottable = this.categories.filter((category) => {
        return !category.is_legacy && ['scatter', 'values'].includes(category.default_representation) && category.type != 'string'
      })

      let custom = this.groups.filter((group) => {
        return group.categories.some((category_name) => {
          return plottable.filter((category) => category.name == category_name).length > 0
        })
      })

      console.log("custom", custom)

      let not_custom = plottable.filter((category) => {
        return !this.groups.some((group) => {
          return group.categories.includes(category.name)
        })
      })

      not_custom.forEach((category) => {
        custom.push({
          "title": category.description,
          "categories": [category.name]
        })
      })

      return custom
    }

  },
  methods: {
    load_report: function (params) {
      Event.fire('load-report', params)
    },
    load_graph: function (params) {
      let data = {
        group: params,
        dates: [new Date(moment().add(-14, 'days').format('YYYY-MM-DD')), new Date(moment().format('YYYY-MM-DD'))]
      }
      Event.fire('load-graph', data)
    },
    load_heatmap: function (params) {
      let data = {
        group: params,
        dates: [new Date(moment().add(-14, 'days').format('YYYY-MM-DD')), new Date(moment().format('YYYY-MM-DD'))]
      }
      Event.fire('load-heatmap', data)
    }
  },
  mounted() {
    if (window.OBJECT_ID) {
      try {
        let data = this.categories.filter(c => c.id == window.OBJECT_ID)
        if (data.length) {
          let name = data[0].name;
          let params = this.plottable_categories.filter(c => c.categories.includes(name))[0];
          let data = {
            group: params,
            dates: [new Date(moment().add(-14, 'days').format('YYYY-MM-DD')), new Date(moment().format('YYYY-MM-DD'))]
          }

          Event.fire('load-graph', data);
        }
      } catch (e) {
        console.log(e);
      }
    }
  }
}
</script>

<style scoped>

</style>