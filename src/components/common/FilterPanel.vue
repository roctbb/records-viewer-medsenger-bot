<template>
    <div>
        <div v-if="!mobile">
            <div class="row">
                <!-- Период -->
                <select class="col form-control form-control-sm" style="height: 34px"
                        v-model="dates.period" @change="select_period()">
                    <option :value="30" :disabled="!dates.range[1]">Месяц</option>
                    <option :value="14" :disabled="!dates.range[1]">Две недели</option>
                    <option :value="7" :disabled="!dates.range[1]">Неделя</option>
                    <option :value="3" :disabled="!dates.range[1]">Три дня</option>
                    <option :value="1" :disabled="!dates.range[1]">День</option>
                    <option :value="-1" v-if="!page.includes('heatmap')">Все данные</option>
                    <option :value="undefined" disabled>Период не выбран</option>
                </select>

                <!-- Даты -->
                <div>
                    <button class="btn btn-default btn-sm"
                            @click="scroll_dates(true)" :disabled="dates.range.some(d => !d)">
                        &#8592;
                    </button>

                    <date-picker :class="`${page}${page == 'report' && window_mode == 'settings' ? '-settings' : ''}`"
                                 format="c DD.MM.YYYY" v-model="dates.range[0]" @change="select_dates(0)"/>
                    <date-picker :class="`${page}${page == 'report' && window_mode == 'settings' ? '-settings' : ''}`"
                                 format="по DD.MM.YYYY" v-model="dates.range[1]" @change="select_dates(1)"/>

                    <button class="btn btn-default btn-sm"
                            @click="scroll_dates(false)" :disabled="dates.range.some(d => !d)">
                        &#8594;
                    </button>
                </div>

                <!-- PDF -->
                <button class="btn btn-sm btn-default" :disabled="disable_downloading"
                        @click="generate_report()">Скачать PDF
                </button>

                <!-- Назад -->
                <a class="btn btn-sm btn-danger" v-if="!object_id" @click="go_back()" href="#">Назад</a>
            </div>

            <!-- Настройки графика -->
            <div v-if="constants.graph_types.includes(page)">
                <input type="checkbox" id="hide_legend" v-model="legend_mode"
                       @change="change_mode('legend', !legend_mode)"/>
                <label for="hide_legend">Скрыть легенду</label>

                <input type="checkbox" id="collapse_points_median" v-model="median_mode"
                       @change="change_mode('points-median', median_mode)" v-if="options && !options.disable_averaging"/>
                <label for="collapse_points_median" v-if="options && !options.disable_averaging">Медиана</label>

                <input type="checkbox" id="collapse_points_sma" v-model="sma_mode"
                       @change="change_mode('points-sma', sma_mode)" v-if="options && !options.disable_averaging"/>
                <label for="collapse_points_sma" v-if="options && !options.disable_averaging">Скользящая средняя (7 дней)</label>

                <input type="checkbox" id="show_points_colors" v-model="colors_mode"
                       @change="change_mode('points-colors', colors_mode)" v-if="options && options.enable_dots_colors"/>
                <label for="show_points_colors" v-if="options && options.enable_dots_colors">Показать цветовые зоны</label>

                <br>
                <small class="text-muted">* Прокрутите страницу вниз для подробной информации</small>
            </div>

            <!-- Настройки суточного -->
            <div v-if="constants.day_graph_types.includes(page)">
                <input type="checkbox" id="hide_legend" v-model="legend_mode"
                       @change="change_mode('legend', !legend_mode)"/>
                <label for="hide_legend">Скрыть легенду</label>
                <br>
                <small class="text-muted">* Прокрутите страницу вниз для подробной информации</small>
            </div>

            <!-- Тепловая карта -->
            <div v-if="options && options.has_additional" style="padding-top: 5px;">
                <input type="checkbox" id="show_optional" @change="change_mode('optional', optional_mode)"
                       v-model="optional_mode"/>
                <label for="show_optional">Показать дополнительные категории</label>

                <br>
                <small class="text-muted">* Прокрутите страницу вниз для подробной информации</small>
            </div>

            <!-- Категории -->
            <div v-if="page == 'report' && categories">
                <multiselect v-model="selected_categories" :options="category_groups" :multiple="true"
                             :close-on-select="false" :clear-on-select="false" :preserve-search="true"
                             group-values="categories" group-label="group" :group-select="true"
                             label="description" track-by="description"
                             placeholder="Введите название категории..."
                             select-label="Выбрать" selected-label="Выбрано" select-group-label="Выбрать всю группу"
                             deselect-group-label="Убрать всю группу" deselect-label="Убрать"
                             @input="update_categories"></multiselect>
            </div>
        </div>

        <!-- Мобильная версия -->
        <div v-else>
            <div class="row">
                <button class="btn btn-sm btn-danger" @click="go_back()" v-if="!object_id && window_mode == 'settings'">
                    Назад
                </button>
                <!-- Период -->
                <select class="col form-control form-control-sm" v-model="dates.period" @change="select_period()">
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
            <div class="row">
                <button class="btn btn-default btn-sm" @click="scroll_dates(true)"
                        :disabled="dates.range.some(d => !d)">
                    &#8592;
                </button>

                <date-picker class="col" format="c DD.MM.YYYY" placeholder="Выбрать начало периода"
                             v-model="dates.range[0]"
                             @change="select_dates(0)"/>
                <date-picker class="col" format="по DD.MM.YYYY" placeholder="Выбрать конец периода"
                             v-model="dates.range[1]"
                             @change="select_dates(1)"/>

                <button class="btn btn-default btn-sm" @click="scroll_dates(false)"
                        :disabled="dates.range.some(d => !d)">
                    &#8594;
                </button>
            </div>

            <!-- Категории -->
            <div v-if="page == 'report' && categories">
                <multiselect v-model="selected_categories" :options="category_groups" :multiple="true"
                             :close-on-select="false" :clear-on-select="false" :preserve-search="true"
                             group-values="categories" group-label="group" :group-select="true"
                             label="description" track-by="description"
                             placeholder="Введите название категории..."
                             select-label="Выбрать" selected-label="Выбрано" select-group-label="Выбрать всю группу"
                             deselect-group-label="Убрать всю группу" deselect-label="Убрать"
                             @input="update_categories"></multiselect>
            </div>

            <!-- Настройки графика -->
            <div v-if="constants.graph_types.includes(page)">
                <input type="checkbox" class="mobile-checkbox" id="hide_legend_mobile" v-model="legend_mode"
                       @change="change_mode('legend', !legend_mode)"/>
                <label for="hide_legend_mobile">Скрыть легенду</label>
                <br>
                <input type="checkbox" class="mobile-checkbox" id="collapse_points_median_mobile" v-model="median_mode"
                       @change="change_mode('points-median', median_mode)" v-if="options && !options.disable_averaging"/>
                <label for="collapse_points_median_mobile"
                       v-if="options && !options.disable_averaging">Медиана</label>
                <br>
                <input type="checkbox" class="mobile-checkbox" id="collapse_points_sma_mobile" v-model="sma_mode"
                       @change="change_mode('points-sma', sma_mode)" v-if="options && !options.disable_averaging"/>
                <label for="collapse_points_sma_mobile" v-if="options && !options.disable_averaging">Скользящая средняя (7 дней)</label>
                <br>
                <input type="checkbox" class="mobile-checkbox" id="show_points_colors_mobile" v-model="colors_mode"
                       @change="change_mode('points-colors', colors_mode)" v-if="options && options.enable_dots_colors"/>
                <label for="show_points_colors_mobile" v-if="options && options.enable_dots_colors">Показать цветовые зоны</label>
                <br>
                <small class="text-muted">* Прокрутите страницу вниз для подробной информации</small>
            </div>

            <!-- Настройки суточного -->
            <div v-if="constants.day_graph_types.includes(page)">
                <input type="checkbox" id="hide_legend" v-model="legend_mode"
                       @change="change_mode('legend', !legend_mode)"/>
                <label for="hide_legend">Скрыть легенду</label>
                <br>
                <small class="text-muted">* Прокрутите страницу вниз для подробной информации</small>
            </div>

            <!-- Тепловая карта -->
            <div v-if="options && options.has_additional">
                <input type="checkbox" class="mobile-checkbox" id="show_optional_mobile"
                       @change="change_mode('optional', optional_mode)"
                       v-model="optional_mode"/>
                <label for="show_optional_mobile">Показать дополнительные категории</label>

                <br>
                <small class="text-muted">* Прокрутите страницу вниз для подробной информации</small>
            </div>
        </div>
    </div>
</template>

<script>
import * as moment from "moment/moment";
import DatePicker from 'vue2-datepicker';
import Multiselect from 'vue-multiselect'
import 'vue2-datepicker/index.css';
import 'vue2-datepicker/locale/ru';

export default {
    name: "FilterPanel",
    props: ['data', 'categories', 'page', 'disable_downloading', 'patient', 'last_date', 'options'],
    components: {DatePicker, Multiselect},
    data() {
        return {
            dates: undefined,
            category: undefined,
            selected_categories: [],
            legend_mode: false,
            median_mode: false,
            sma_mode: false,
            colors_mode: false,
            optional_mode: false,
            show_collapse: false
        }
    },
    computed: {
        category_groups() {
            let groups = []
            Object.entries(this.group_by(this.categories, 'subcategory')).forEach(([group, categories]) => {
                groups.push({
                    group: group,
                    categories: categories
                })
            })
            return groups
        }
    },
    methods: {
        generate_report: function () {
            Event.fire('generate-report')
        },
        update_dates: function () {
            let action = (['report', 'formalized-report'].includes(this.page) ? this.page : 'graph') + '-update-dates'
            this.dates.range = [
                this.dates.range[0] ? this.start_of_day(this.dates.range[0]) : undefined,
                this.dates.range[1] ? this.end_of_day(this.dates.range[1]) : undefined
            ]
            Event.fire(action, this.dates.range)
        },
        update_categories: function (value) {
            Event.fire('update-categories', this.selected_categories)
        },
        change_mode: function (target, mode) {
            if (target.includes('points')) {
                Event.fire('update-points', {mode: mode, target: target.replace('points-', '')})
            } else {
                Event.fire('update-' + target, mode)
            }
        },
        scroll_dates: function (back) {
            let duration = this.dates_difference(this.dates.range[0], this.dates.range[1])
            if (this.page.includes('heatmap') && duration > 30) return

            if (this.dates.range[0] <= this.dates.range[1]) {
                this.dates.range[0] = this.add_days(this.dates.range[0], (back ? -1 : 1) * duration)
                this.dates.range[1] = this.add_days(this.dates.range[1], (back ? -1 : 1) * duration)
            }

            this.$forceUpdate()
            this.update_dates()
        },
        select_dates: function (index) {
            this.dates.range[index] = index ?
                this.end_of_day(this.dates.range[index]) :
                this.start_of_day(this.dates.range[index])
            if (!this.dates.range.some(d => d == undefined)) {
                let duration = this.dates_difference(this.dates.range[0], this.dates.range[1])
                this.dates.period = [30, 14, 7, 3, 1].includes(duration) ? duration : undefined

                if (this.dates.range[0] > this.dates.range[1]) duration *= -1
                if (duration < 0 || this.page.includes('heatmap') && duration > 30) {
                    Event.fire('incorrect-dates', duration)
                    return
                }
            }

            this.$forceUpdate()
            this.update_dates()
        },
        select_period: function () {
            if (!this.dates.period) return
            if (this.dates.period > 0) {
                this.dates.range[0] = this.start_of_day(this.add_days(this.dates.range[1], -this.dates.period + 1))
            } else {
                this.dates.range = [undefined, this.end_of_day(new Date())]
            }
            this.update_dates()
        },
        go_back: function () {
            Event.fire('back-to-dashboard')
        }
    },
    created() {
        console.log('filter-panel created', this.page)
        this.dates = {
            range: [],
            period: undefined,
        }

        Event.listen('load-report', params => {
            this.dates.range = [undefined, this.last_date]
            this.dates.period = -1
        })


        Event.listen('back-to-dashboard', () => {
            this.legend_mode = false
            this.median_mode = false
            this.sma_mode = false
            this.medicines_mode = false
        });

        Event.listen('show-collapse', mode => {
            this.show_collapse = mode
            this.$forceUpdate()
        })

        Event.listen('set-points-mode', (data) => {
            this[data.target + '_mode'] = data.mode
            this.$forceUpdate()
        })

        Event.listen('set-dates', (dates) => {
            this.dates.range = [
                dates[0] ? this.start_of_day(dates[0]) : undefined,
                dates[1] ? this.end_of_day(dates[1]) : undefined
            ]

            let duration = this.dates_difference(this.dates.range[0], this.dates.range[1])
            this.dates.period = [30, 14, 7, 3, 1].includes(duration) ? duration : undefined

            this.$forceUpdate()
        })
    }

}
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style scoped>
.multiselect__tag {
    white-space: unset;
    margin-bottom: 0;
}

.multiselect__option {
    white-space: unset;
}

.row {
    margin-bottom: 5px;
    grid-column-gap: 5px;
}

.btn {
    height: 34px;
}

.mobile-checkbox {
    margin: 0 5px 0 0;
}

input[type="checkbox" i] {
    margin: 0 5px 0 2px;
}

label {
    margin-bottom: 0;
    margin-right: 15px;
}
</style>