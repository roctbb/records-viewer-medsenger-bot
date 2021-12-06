<template>
  <div>
    <form v-if="mobile">
      <!-- Даты -->
      <div class="form-group row" style="margin-left: 0;grid-column-gap: 30px;">
        <date-picker format="c DD.MM.YYYY" v-model="dates.range[0]" @change="select_dates()"></date-picker>
        <date-picker format="по DD.MM.YYYY" v-model="dates.range[1]" @change="select_dates()"></date-picker>
      </div>
      <div class="form-group row" style="margin-left: 0">
        <button class="btn btn-primary btn-sm" @click="scroll_dates(true)">&#8592;</button>
        <button class="btn btn-primary btn-sm" @click="scroll_dates(false)">&#8594;</button>
      </div>
      <div class="form-group row">
        <label class="col-sm-1 col-form-label">Период:</label>
        <div :class="mobile ? 'col' :'col-4'">
          <select class="form-control form-control-sm" v-model="dates.period" @change="select_period()">
            <option :value="30">Месяц</option>
            <option :value="14">Две недели</option>
            <option :value="7">Неделя</option>
            <option :value="3">Три дня</option>
            <option :value="1">День</option>
            <option :value="undefined">Не выбран</option>
          </select>
        </div>
      </div>
      <!-- Категории -->
      <div class="form-group row">
        <label for="category" class="col-sm-1 col-form-label">Категория:</label>
        <div class="col">
          <select class="form-control form-control-sm" v-model="category" @change="update_category()">
            <option :value="undefined">Не выбрана</option>
            <optgroup v-for="(group, name) in group_by(category_list, 'subcategory')" :label="name">
              <option v-for="category in group" :value="category.name">{{ category.description }}</option>
            </optgroup>
          </select>
        </div>
      </div>
    </form>


    <div class="row" v-else>
      <form class="col-5">
        <div class="form-group row" style="grid-column-gap: 0;">
          <label class="col-1 col-form-label">Период:</label>
          <div class="col offset-2">
            <select class="form-control form-control-sm" v-model="dates.period" @change="select_period()">
              <option :value="30">Месяц</option>
              <option :value="14">Две недели</option>
              <option :value="7">Неделя</option>
              <option :value="3">Три дня</option>
              <option :value="1">День</option>
              <option :value="undefined">Не выбран</option>
            </select>
          </div>
        </div>
        <!-- Категории -->
        <div class="form-group row" style="grid-column-gap: 0;">
          <label class="col-sm-1 col-form-label">Категория:</label>
          <div class="col offset-2">
            <select class="form-control form-control-sm" id="category" v-model="category"  @change="update_category()">
              <option :value="undefined">Не выбрана</option>
              <optgroup v-for="(group, name) in group_by(category_list, 'subcategory')" :label="name">
                <option v-for="category in group" :value="category.name">{{ category.description }}</option>
              </optgroup>
            </select>
          </div>
        </div>
      </form>
      <form class="col">
        <!-- Даты -->
        <div class="form-group row" style="margin-left: 0;">
          <date-picker format="c DD.MM.YYYY" v-model="dates.range[0]" @change="select_dates()"></date-picker>
          <date-picker format="по DD.MM.YYYY" v-model="dates.range[1]" @change="select_dates()"></date-picker>
        </div>
        <div class="form-group row" style="margin-left: 0">
          <button class="btn btn-primary btn-sm" @click="scroll_dates(true)">&#8592;</button>
          <button class="btn btn-primary btn-sm" @click="scroll_dates(false)">&#8594;</button>
        </div>
      </form>
    </div>

    <!--
    <div>
      <input class="btn btn-link" type="button" data-toggle="collapse" aria-expanded="false"
             value="+ Выбрать категории" data-target="#collapse" aria-controls="collapse" style="margin-left: -5px">
      <div class="collapse" id="collapse">
        <div class="card card-body">

          <div class="row">
            <div v-for="(category, i) in category_list">
              <input type="checkbox" :id="category.name" @change="update_categories()" v-model="category_choice[i]"/>
              <label :for="category.name">{{ category.description }}</label>
            </div>
          </div>

        </div>
      </div>
    </div>
    -->

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
  props: ['data'],
  components: {DatePicker, ErrorBlock},
  data() {
    return {
      dates: [],
      errors: [],
      category: undefined
      // category_choice: [],
    }
  },
  methods: {
    update_dates: function () {
      Event.fire('update-dates', this.dates.range)
    },
    update_categories: function () {
      let chosen = this.category_list.filter((category, index) => this.category_choice[index])
      Event.fire('update-categories', chosen)
    },
    update_category: function () {
      Event.fire('update-category', this.category)
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
      let duration = moment(this.dates.range[1]).diff(moment(this.dates.range[0]), 'day')
      this.dates.period = [30, 14, 7, 3, 1].includes(duration) ? duration : -1

      this.$forceUpdate()
      this.update_dates()
    },
    select_period: function () {
      let end = moment(this.dates.range[1])
      this.dates.range[0] = new Date(end.add(-this.dates.period, 'days').format('YYYY-MM-DD'))
      this.update_dates()
    },
    group_by: function (categories, field) {
      return categories.reduce((groups, item) => {
        const group = (groups[item[field]] || []);
        group.push(item);
        groups[item[field]] = group;
        return groups;
      }, {});
    }
  },
  created() {
    this.dates = {
      range: [undefined, new Date(moment().format('YYYY-MM-DD'))],
      period: undefined,
    }

    // this.category_choice = this.category_list.map(() => false)
  }

}
</script>

<style scoped>
.row {
  grid-column-gap: 10px;
  margin-bottom: 5px;
}

.card-body {
  background-color: transparent;
  border-color: transparent;
}
</style>