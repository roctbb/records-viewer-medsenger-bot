<template>
  <div>
    <div v-if="!mobile" style="margin: 0 15px">
      <div class="row">
        <button class="btn btn-sm btn-danger col-sm-1" @click="go_back()" v-if="!object_id && window_mode == 'settings'">Назад
        </button>

        <!-- Период -->
        <div class="col" :style="window_mode != 'settings' ? 'margin-left: -15px' : ''">
          <select class="form-control form-control-sm" v-model="dates.period" @change="select_period()">
            <option :value="30" :disabled="!dates.range[1]">Месяц</option>
            <option :value="14" :disabled="!dates.range[1]">Две недели</option>
            <option :value="7" :disabled="!dates.range[1]">Неделя</option>
            <option :value="3" :disabled="!dates.range[1]">Три дня</option>
            <option :value="1" :disabled="!dates.range[1]">День</option>
            <option :value="-1">Все данные</option>
            <option :value="undefined" disabled>Период не выбран</option>
          </select>
        </div>
        <!-- Даты -->
        <div>
          <button class="btn btn-primary btn-sm" @click="scroll_dates(true)" :disabled="dates.range.some(d => !d)">
            &#8592;
          </button>

          <date-picker format="c DD.MM.YYYY" v-model="dates.range[0]" @change="select_dates()"/>
          <date-picker format="по DD.MM.YYYY" v-model="dates.range[1]" @change="select_dates()"/>

          <button class="btn btn-primary btn-sm" @click="scroll_dates(false)" :disabled="dates.range.some(d => !d)">
            &#8594;
          </button>
        </div>

        <!-- Показать легенду -->
        <div v-if="page == 'graph'" style="padding-top: 5px;">
          <input type="checkbox" id="hide_legend" v-model="mode" @change="change_mode('legend')"/>
          <label for="hide_legend">Скрыть легенду</label>
        </div>

        <!-- Тепловая карта -->
        <div v-if="page == 'symptoms-heatmap'" style="padding-top: 5px;">
          <input type="checkbox" id="show_medicines" @change="change_mode('medicines')" v-model="mode"/>
          <label for="show_medicines">Показать лекарства</label>
        </div>

        <!-- Отчет -->
        <button class="btn btn-sm btn-primary" v-if="page == 'report'" :disabled="disable_downloading"
                @click="generate_report()">Скачать PDF
        </button>
      </div>

      <!-- Категории -->
      <div class="row" v-if="page == 'report' && categories">
        <div :class="`${window_mode == 'report' ? '' : 'offset-1'} col`"
             :style="`padding-left: ${window_mode == 'report' ? 0 : 25}px; padding-right: 0px`">
          <select class="form-control form-control-sm" v-model="category" @change="update_category()">
            <option :value="undefined">Категория не выбрана</option>
            <optgroup v-for="(group, name) in group_by(categories, 'subcategory')" :label="name">
              <option v-for="category in group" :value="category.name">{{ category.description }}</option>
            </optgroup>
          </select>
        </div>
      </div>
    </div>

    <!-- Мобильная версия -->
    <div v-else>
      <div class="row" :style="`margin-left: ${window_mode != 'settings' ? -15 : 0}px`">
        <button class="btn btn-sm btn-danger" @click="go_back()" v-if="!object_id && window_mode == 'settings'">Назад</button>
        <!-- Период -->
        <div class="col">
          <select class="form-control form-control-sm" v-model="dates.period" @change="select_period()">
            <option :value="30" :disabled="!dates.range[1]">Месяц</option>
            <option :value="14" :disabled="!dates.range[1]">Две недели</option>
            <option :value="7" :disabled="!dates.range[1]">Неделя</option>
            <option :value="3" :disabled="!dates.range[1]">Три дня</option>
            <option :value="1" :disabled="!dates.range[1]">День</option>
            <option :value="-1">Все данные</option>
            <option :value="undefined" disabled>Период не выбран</option>
          </select>
        </div>
      </div>

      <!-- Даты -->
      <div class="row" style="margin-left: -15px; column-gap: 0">
        <date-picker class="col" format="c DD.MM.YYYY" placeholder="Выбрать начало периода" v-model="dates.range[0]" @change="select_dates()"/>
        <date-picker class="col" format="по DD.MM.YYYY" placeholder="Выбрать конец периода" v-model="dates.range[1]" @change="select_dates()"/>
      </div>

      <div class="row" style="margin-left: 0">
        <button class="btn btn-primary btn-sm" @click="scroll_dates(true)" :disabled="dates.range.some(d => !d)">
          &#8592;
        </button>
        <button class="btn btn-primary btn-sm" @click="scroll_dates(false)" :disabled="dates.range.some(d => !d)">
          &#8594;
        </button>

        <!-- Показать легенду -->
        <div v-if="page == 'graph'" style="padding-top: 5px;">
          <input type="checkbox" id="hide_legend_mobile" v-model="mode" @change="change_mode('legend')"/>
          <label for="hide_legend_mobile">Скрыть легенду</label>
        </div>

        <!-- Тепловая карта -->
        <div v-if="page == 'symptoms-heatmap'" style="padding-top: 5px;">
          <input type="checkbox" id="show_medicines_mobile" @change="change_mode('medicines')" v-model="mode"/>
          <label for="show_medicines_mobile">Показать лекарства</label>
        </div>

        <!-- Категории -->
        <div class="col" v-if="page == 'report' && categories">
          <select class="form-control form-control-sm" v-model="category" @change="update_category()">
            <option :value="undefined">Категория не выбрана</option>
            <optgroup v-for="(group, name) in group_by(categories, 'subcategory')" :label="name">
              <option v-for="category in group" :value="category.name">{{ category.description }}</option>
            </optgroup>
          </select>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import * as moment from "moment/moment";
import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';
import 'vue2-datepicker/locale/ru';

export default {
  name: "FilterPanel",
  props: ['data', 'categories', 'page', 'disable_downloading'],
  components: {DatePicker},
  data() {
    return {
      dates: undefined,
      category: undefined,
      mode: false
      // category_choice: [],
    }
  },
  methods: {
    go_back: function () {
      Event.fire('back-to-dashboard')
    },
    generate_report: function () {
      Event.fire('generate-report')
    },
    update_dates: function () {
      let action = (this.page == 'report' ? this.page : 'graph') + '-update-dates'
      Event.fire(action, this.dates.range)
    },
    update_category: function () {
      Event.fire('update-category', this.category)
    },
    change_mode: function (target) {
      Event.fire('update-' + target, !this.mode)
    },
    scroll_dates: function (back) {
      let start = moment(this.dates.range[0])
      let end = moment(this.dates.range[1])
      let duration = end.diff(start, 'day')

      if (end > start) {
        this.dates.range[0] = new Date(start.add((back ? -1 : 1) * duration, 'days').format('YYYY-MM-DD'))
        this.dates.range[1] = new Date(end.add((back ? -1 : 1) * duration, 'days').format('YYYY-MM-DD'))
      }

      this.$forceUpdate()
      this.update_dates()
    },
    select_dates: function () {
      if (!this.dates.range.some(d => d == undefined)) {
        let duration = moment(this.dates.range[1]).diff(moment(this.dates.range[0]), 'day')
        this.dates.period = [30, 14, 7, 3, 1].includes(duration) ? duration : undefined

        if (duration < 0) {
          Event.fire('incorrect-dates')
          return
        }
      }

      this.$forceUpdate()
      this.update_dates()
    },
    select_period: function () {
      if (this.dates.period > 0) {
        let end = moment(this.dates.range[1])
        this.dates.range[0] = new Date(end.add(-this.dates.period, 'days').format('YYYY-MM-DD'))
      } else {
        this.dates.range = [undefined, new Date()]
      }
      this.update_dates()
    },
    group_by: function (categories, field) {
      if (!this.categories)
        return []

      return this.categories.reduce((groups, item) => {
        const group = (groups[item[field]] || []);
        group.push(item);
        groups[item[field]] = group;
        return groups;
      }, {});
    }
  },
  created() {
    let range = this.page == 'report' ?
        [undefined, new Date(moment().format('YYYY-MM-DD'))] :
        [new Date(moment().add(-14, 'days').format('YYYY-MM-DD')), new Date(moment().format('YYYY-MM-DD'))]
    this.dates = {
      range: range,
      period: this.page == 'report' ? undefined : 14,
    }

    Event.listen('back-to-dashboard', () => {
      this.dates = {
        range: range,
        period: this.page == 'report' ? undefined : 14,
      }
      this.mode = false
    });

    Event.listen('set-start-date', date => {
      this.dates.range[0] = date
      this.$forceUpdate()
    })
  }

}
</script>

<style scoped>
.row {
  grid-column-gap: 10px;
  margin-bottom: 5px;
}
</style>