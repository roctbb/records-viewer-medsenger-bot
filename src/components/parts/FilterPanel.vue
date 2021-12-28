<template>
  <div>
    <div class="form-group row" style="margin-left: 0">
      <button class="btn btn-sm btn-danger" @click="go_back()" v-if="!object_id && window_mode != 'report'">Назад</button>
      <button class="btn btn-sm btn-primary" v-if="!mobile && page == 'report'" :disabled="disable_downloading"
              @click="generate_report()">Скачать PDF
      </button>

      <!-- Категории -->
      <label class="col-1 col-form-label" v-if="!mobile && page == 'report'">Категория:</label>
      <div class="col" v-if="!mobile && page == 'report'" style="margin-left: 10px">
        <select class="form-control form-control-sm" id="category" v-model="category" @change="update_category()">
          <option :value="undefined">Не выбрана</option>
          <optgroup v-for="(group, name) in group_by(categories, 'subcategory')" :label="name">
            <option v-for="category in group" :value="category.name">{{ category.description }}</option>
          </optgroup>
        </select>
      </div>

      <!-- Показать легенду -->
      <div v-if="page == 'graph'" :style="object_id ? '' : 'margin-left: 25px'">
        <input type="checkbox" id="hide_legend" v-model="mode" @change="change_mode('legend')"/>
        <label for="hide_legend">Скрыть легенду</label>
      </div>

      <!-- Тепловая карта -->
      <div v-if="page == 'symptoms-heatmap'" :style="object_id ? '' : 'margin-left: 25px'">
        <input type="checkbox" id="show_medicines" @change="change_mode('medicines')" v-model="mode"/>
        <label for="show_medicines">Показать лекарства</label>
      </div>

    </div>

    <div v-if="mobile">
      <!-- Даты -->
      <div class="form-group row" style="margin-left: 0;grid-column-gap: 30px;">
        <date-picker format="c DD.MM.YYYY" v-model="dates.range[0]" @change="select_dates()"></date-picker>
        <date-picker format="по DD.MM.YYYY" v-model="dates.range[1]" @change="select_dates()"></date-picker>
      </div>
      <div class="form-group row" style="margin-left: 0">
        <button class="btn btn-primary btn-sm" @click="scroll_dates(true)" :disabled="dates.range.some(d => !d)">
          &#8592;
        </button>
        <button class="btn btn-primary btn-sm" @click="scroll_dates(false)" :disabled="dates.range.some(d => !d)">
          &#8594;
        </button>
      </div>
      <div class="form-group row">
        <label class="col-sm-1 col-form-label">Период:</label>
        <div :class="mobile ? 'col' :'col-4'">
          <select class="form-control form-control-sm" v-model="dates.period" @change="select_period()">
            <option :value="30" :disabled="!dates.range[1]">Месяц</option>
            <option :value="14" :disabled="!dates.range[1]">Две недели</option>
            <option :value="7" :disabled="!dates.range[1]">Неделя</option>
            <option :value="3" :disabled="!dates.range[1]">Три дня</option>
            <option :value="1" :disabled="!dates.range[1]">День</option>
            <option :value="-1">Все данные</option>
            <option :value="undefined" disabled>Не выбран</option>
          </select>
        </div>
      </div>
      <!-- Категории -->
      <div class="form-group row" v-if="categories">
        <label for="category" class="col-sm-1 col-form-label">Категория:</label>
        <div class="col">
          <select class="form-control form-control-sm" v-model="category" @change="update_category()">
            <option :value="undefined">Не выбрана</option>
            <optgroup v-for="(group, name) in group_by(categories, 'subcategory')" :label="name">
              <option v-for="category in group" :value="category.name">{{ category.description }}</option>
            </optgroup>
          </select>
        </div>
      </div>
    </div>


    <div class="row" v-else>

      <div class="col-4">
        <div class="form-group row" style="grid-column-gap: 0;">
          <label class="col-1 col-form-label">Период:</label>
          <div class="col offset-2">
            <select class="form-control form-control-sm" v-model="dates.period" @change="select_period()">
              <option :value="30" :disabled="!dates.range[1]">Месяц</option>
              <option :value="14" :disabled="!dates.range[1]">Две недели</option>
              <option :value="7" :disabled="!dates.range[1]">Неделя</option>
              <option :value="3" :disabled="!dates.range[1]">Три дня</option>
              <option :value="1" :disabled="!dates.range[1]">День</option>
              <option :value="-1">Все данные</option>
              <option :value="undefined" disabled>Не выбран</option>
            </select>
          </div>
        </div>
      </div>
      <!-- Даты -->
      <div class="col">
        <button class="btn btn-primary btn-sm" @click="scroll_dates(true)" :disabled="dates.range.some(d => !d)">
          &#8592;
        </button>

        <date-picker format="c DD.MM.YYYY" v-model="dates.range[0]" @change="select_dates()"></date-picker>
        <date-picker format="по DD.MM.YYYY" v-model="dates.range[1]" @change="select_dates()"></date-picker>

        <button class="btn btn-primary btn-sm" @click="scroll_dates(false)" :disabled="dates.range.some(d => !d)">
          &#8594;
        </button>
      </div>
    </div>

    <!-- Ошибки -->
    <error-block :errors="errors" v-if="errors.length"></error-block>
  </div>
</template>

<script>
import * as moment from "moment/moment";
import DatePicker from 'vue2-datepicker';
import 'vue2-datepicker/index.css';
import 'vue2-datepicker/locale/ru';
import ErrorBlock from "./ErrorBlock";

export default {
  name: "FilterPanel",
  props: ['data', 'categories', 'page', 'disable_downloading'],
  components: {DatePicker, ErrorBlock},
  data() {
    return {
      dates: undefined,
      errors: [],
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