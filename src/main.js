import Vue from 'vue'
import App from './App.vue'
import vmodal from 'vue-js-modal'
import VueConfirmDialog from 'vue-confirm-dialog'
import VueEllipseProgress from 'vue-ellipse-progress';
import * as moment from "moment";

window.Event = new class {
    constructor() {
        this.vue = new Vue();
    }

    fire(event, data = null) {
        if (!data) {
            console.log('sending event', event);
        } else {
            console.log('sending event', event, 'with data', data);
        }

        this.vue.$emit(event, data);
    }

    listen(event, callback) {
        this.vue.$on(event, callback);
    }
};

Vue.mixin({
    methods: {
        delay: function (time) {
            return new Promise(resolve => setTimeout(resolve, time));
        },
        br: function (doc) {
            if (!doc) return doc;
            return doc.replace(/([^>])\n/g, '$1<br/>')
        },
        // urls
        url: function (action, agent_id) {
            let api_host = window.API_HOST;
            let agent_token = window.AGENT_TOKEN;
            let contract_id = window.CONTRACT_ID;

            if (!agent_id) {
                agent_id = window.AGENT_ID;
            }


            return api_host + '/api/client/agents/' + agent_id + '/?action=' + action + '&contract_id=' + contract_id + '&agent_token=' + agent_token
        },
        direct_url: function (action) {
            let host = window.LOCALHOST;
            let agent_token = window.AGENT_TOKEN;
            let contract_id = window.CONTRACT_ID;
            let agent_id = window.AGENT_ID;

            return host + action + '?contract_id=' + contract_id + '&agent_token=' + agent_token
        },
        image_url: function (file_name) {
            return 'https://common.medsenger.ru/images/' + file_name
        },

        // data
        group_by: function (data, field) {
            if (!data)
                return []

            return data.reduce((groups, item) => {
                const group = (groups[item[field] != undefined ? item[field] : 'Общее'] || []);
                group.push(item);
                groups[item[field] != undefined ? item[field] : 'Общее'] = group;
                return groups;
            }, {});
        },
        group_records_by_categories_by_dates: function (records, by_categories = false) {
            let records_by_categories = by_categories ?
                records :
                this.group_by(records, 'category_code')
            let records_by_categories_by_dates = {}

            Object.entries(records_by_categories).forEach(([category, records]) => {
                records_by_categories_by_dates[category] = this.group_by(records, 'formatted_date')
            })
            return records_by_categories_by_dates
        },
        get_record_groups: function (records, get_comments = false) {
            let records_by_groups = this.group_by(records, 'group')

            let groups = []

            Object.entries(records_by_groups).forEach(([uid, group_records]) => {

                let group = {
                    records: group_records,
                    records_by_categories: this.group_by(group_records, 'category_code'),
                    timestamp: group_records[0].timestamp,
                    formatted_date: group_records[0].formatted_date,
                    formatted_time: group_records[0].formatted_time
                }

                groups.push(group)
            })

            groups.forEach((group) => {
                if (get_comments) {
                    group.comments = []
                    group.records.forEach((record) => {
                        group.comments = group.comments
                            .concat(record.comments)
                            .filter((comment => comment))
                    })
                }
            })
            groups.sort((a, b) => a.timestamp - b.timestamp)

            return groups
        },
        filter_groups: function (records, categories, group_filters) {
            let get_comments = 'comments' in group_filters
            let groups = this.get_record_groups(records, get_comments)


            groups.forEach((group) => {
                group.records = group.records
                    .filter((record) => categories.includes(record.category_code))
            })

            if (group_filters) {
                if (group_filters.comments) {
                    groups = groups.filter((group) => group.comments.length)
                }
                if (group_filters.grade != undefined) {
                    groups.forEach((group) => {
                        group.records = group.records.filter((record) =>
                            record.params && record.params.grade == group_filters['grade'])
                    })
                }
                if (group_filters.general_answer) {
                    groups.forEach((group) => {
                        group.records = group.records.filter((record) =>
                            record.params && record.params.general_answer)
                    })
                }
                if (group_filters.other_doctor) {
                    groups.forEach((group) => {
                        group.records = group.records.filter((record) =>
                            record.contract_id != this.contract_id)
                    })
                }
            }

            groups = groups.filter((group) => group.records.length)
            groups.forEach((group) => {
                group.records_by_categories = this.group_by(group.records, 'category_code')
            })

            return groups
        },
        load_data: function (categories, dates, options = null, required_categories = null) {
            let data = {
                categories: categories,
                dates: dates, // [start, end]
                options: options, // {type, first_load, get_pages_count, page}
                required_categories: required_categories ? required_categories : categories
            }

            this.axios.post(this.direct_url('/api/get_records'), data).then(response => {
                response.data.records = response.data.records.map(this.process_record)
                Event.fire('loaded', response.data)

                let data_type = options.type.includes('report') ? options.type : 'graph'
                Event.fire(data_type + '-data-loaded', response.data)
            });
        },
        load_additional_data: function (categories, end_date, period, type) {
            if (period == 0) {
                Event.fire('additional-loaded', [])
                return
            }

            end_date /= 1000
            let start_date = end_date - this.day * period / 1000

            // вытаскиваю предыдущие n дней
            let data = {
                categories: categories,
                dates: [start_date, end_date], // [start, end]
                options: {
                    type: type
                }
            }

            this.axios
                .post(this.direct_url('/api/get_records'), data)
                .then((response) => {
                    let records = response.data.records.map(this.process_record)

                    Event.fire('additional-loaded', records)
                })
        },
        process_record: function (r) {
            r.category_code = r.category_info.name
            r.category_type = r.category_info.type

            let d = new Date(r.timestamp * 1000)
            r.formatted_date = this.format_date(d)
            r.formatted_time = this.format_time(d)
            r.formatted_hours = r.formatted_date + ` ${d.getHours()}:00-${(d.getHours() + 1) % 24}:00`

            return r
        },
        send_order: function (order, agent, params, event_name, returns_records = true) {
            let data = {order: order, agent_id: window.AGENTS[`${agent}_AGENT_ID`], params: params}
            this.axios
                .post(this.url('/send_order'), data)
                .then((response) => {
                    let result = response.data

                    if (order == 'get_compliance') {
                        if (!response.data.forms) response.data.forms = []
                        response.data.forms.forEach((f, i) => {
                            f.category_code = 'form_compliance'
                            f.group = `${f.category_code}_${i}`
                        })

                        if (!response.data.medicines) response.data.medicines = []
                        response.data.medicines.forEach((m, i) => {
                            m.category_code = 'medicine_compliance'
                            m.group = `${m.category_code}_${i}`
                        })

                        result = response.data.forms.concat(response.data.medicines)
                        result = result.filter((r) => r.requested)
                    }

                    if (order == 'get_medicines') {
                        result.forEach((r, i) => {
                            r.category_code = r.is_created_by_patient ? 'added_medicine' : 'prescribed_medicine'
                            r.group = `${r.category_code}_${i}`
                            r.date = new Date(r.prescribed_timestamp * 1000)
                        })
                    }

                    if (order == 'get_form') {
                        result = {
                            record_id: params.record_id,
                            form: result
                        }
                    }

                    if (returns_records) {
                        result = result.map((p, i) => {
                            let d = p.date ? p.date : new Date()

                            p.formatted_date = this.format_date(d)
                            p.formatted_time = this.format_time(d)

                            return p
                        })
                    }

                    Event.fire(event_name, result)
                })
        },

        // values
        binary_search: function (arr, value, l, r) {
            let mid = Math.floor((r - l) / 2) + l

            if (arr[mid] == value)
                return mid;
            if (r - l <= 0)
                return r + (arr[r] >= value ? 0 : 1);

            if (arr[mid] > value) {
                r = (mid - 1) < l ? l : (mid - 1)
                return this.binary_search(arr, value, l, r);
            }
            l = (mid + 1) > r ? r : (mid + 1)
            return this.binary_search(arr, value, l, r);
        },

        copy: function (to, from) {
            Object.keys(from).forEach(k => {
                to[k] = from[k]
            })
        },

        median: function (arr) {
            const arrayHalf = arr.length / 2
            const sorted = [].concat(arr).sort((a, b) => a - b)

            return arr.length % 2 === 0
                ? (sorted[arrayHalf] + sorted[arrayHalf - 1]) / 2
                : sorted[~~(arrayHalf)]
        },
        simple_moving_average: function (data_by_dates, additional_data_by_dates, period, date) {
            let tmp_date = moment(date, 'DD.MM.YYYY').subtract(1, 'day'), values = []
            let filled_days = 0

            let sma_data = {}
            Object.assign(sma_data, data_by_dates, additional_data_by_dates)

            for (let d = 0; d < period; d++) {
                let formatted_date = tmp_date.format('DD.MM.YYYY')

                let tmp_values = sma_data[formatted_date] ?
                    sma_data[formatted_date].map(val => val.value ? val.value : val.y) : []
                if (tmp_values.length) filled_days++

                values = values.concat(tmp_values)
                tmp_date = tmp_date.subtract(1, 'day')
            }

            return {
                value: (values.reduce((a, b) => a + b, 0) / values.length) || 0,
                credible: period == filled_days,
                filled_days: filled_days
            }
        },
        get_color_from_additions(point) {
            let zone = this.zone_addition(point)
            if (zone && zone['color']) {
                return zone['color']
            }
            return this.colors.gray[1]
        },

        // dates
        format_time: function (date) {
            return date.toTimeString().substring(0, 5)
        },
        format_date: function (date) {
            return date.toLocaleDateString()
        },
        add_days: function (date, days) {
            let new_date = new Date(date.valueOf());
            new_date.setDate(new_date.getDate() + days);
            return new_date;
        },
        start_of_day: function (date) {
            date.setHours(0, 0, 0, 0)
            return date
        },
        middle_of_day: function (date) {
            date.setHours(12, 0, 0, 0)
            return date
        },
        end_of_day: function (date) {
            date.setHours(23, 59, 59, 999)
            return date
        },
        dates_difference: function (date1, date2) {
            const diffTime = Math.abs(date2 - date1);
            return Math.ceil(diffTime / this.day)
        },
        range_arr: function (size, startAt = 0) {
            return [...Array(size).keys()].map(i => i + startAt);
        },


        // data processing
        add_error: function (errors, error) {
            errors = this.remove_error(errors, error)
            errors.push(error)
            return errors
        },
        remove_error: function (errors, error) {
            return errors ? errors.filter(e => e != error) : []
        },

        zone_addition: function (record) {
            let zones = record.additions ?
                record.additions.filter((a) => a && a['addition'] && a['addition']['zone_description']) : undefined
            return zones && zones.length ? zones[0]['addition'] : undefined
        },
        comment_additions: function (record) {
            return record.additions ?
                record.additions.filter((a) => a && a['addition'] && a['addition']['comment'] && this.is_warning_addition(a)) : []
        },
        is_warning_addition(addition) {
            return !(addition['addition'] && addition['addition'].show_warning === false)
        },
        color_transparency: function (color, percentage) {
            if (!color) return 'transparent'
            if (color in this.colors) color = this.colors[color][0]

            if (color.includes('rgb')) {
                let p = percentage / 100
                return color.split(',').length == 3 ? color.replace(')', `,${p})`) : color.replace(',1)', `,${p})`)
            } else {
                let dec = (percentage * 255 / 100).toFixed(0) * 1
                let hex = dec.toString(16)
                return color + hex
            }
        }

    },
    computed: {
        mobile() {
            return window.innerWidth < window.innerHeight
        },
        day() {
            return 24 * 36e5
        },
        offset() {
            return -1 * new Date().getTimezoneOffset() * 60
        }
    },
    data() {
        return {
            images: {
                logo: this.image_url('logo.png'),
                ok: this.image_url('icons8-ok-128.png'),
                error: this.image_url('icons8-delete-128.png'),
                nothing_found: this.image_url('icons8-nothing-found-100.png'),
                warning: this.image_url('icons8-error-18.png'),
                report: this.image_url('icons8-search-property-96.png'),
                graph: this.image_url('icons8-graph-96.png'),
                heatmap: this.image_url('icons8-heat-map-96.png'),
                file: this.image_url('icons8-open-document-48.png'),
                yellow_alert: this.image_url('icons8-yellow-alert-96.png'),
                red_alert: this.image_url('icons8-red-alert-96.png'),
                message: this.image_url('icons8-communication-96.png'),
                medicines: this.image_url('icons8-medicines-96.png'),
                fill_form: this.image_url('icons8-fill-in-form-48.png'),
                pills: this.image_url('icons8-pills-96.png'),
                checkmark: this.image_url('icons8-checkmark-96.png'),
                checked: this.image_url('icons8-checked-checkmark-96.png'),
                unchecked: this.image_url('icons8-unchecked-checkmark-96.png')
            },
            error_messages: {
                too_mach_points: 'За данный период в медицинской карте присутствует слишком большое количество записей (> 500). ',
                averaged: 'Для удобства мы усреднили значения. Усреднение можно убрать с помощью галочки выше, но в таком случае точные значения будут недоступны.',
                not_averaged: 'Чтобы увидеть комментарии к точкам и симптомы, загрузите период с меньшим количеством записей или усредните значения.',
                incorrect_period: 'Выбран некорректный период',
                not_more_30_days: 'Пожалуйста, выберите период <b>не больше</b> 30 дней.'
            },
            colors: {
                background: ['#fcfcfc', '#ffffff'],
                medsenger: ['#006c88', '#24a8b4', '#72d6e0'],
                red: ['#dc0909', '#fd1f1f', '#f55353'],
                orange: ['#f16400', '#f67e2a', '#ff9246'],
                yellow: ['#ffc800', '#fbd433', '#fce200'],
                green: ['#50b432', '#4fde21', '#85ef62'],
                blue: ['#058dc7', '#24cbe5', '#36c3ff'],
                darkblue: ['#095cf5', '#3673e8', '#598def'],
                purple: ['#721fff', '#853cff', '#9a63fd'],
                pink: ['#aa27ce', '#c355ff', '#c677f5'],
                gray: ['#646464', '#7d7d7d', '#969696', '#afafaf', '#d3d3d3'],
                scale: ['#50B432', '#73B828', '#96BC1E', '#B9C014',
                    '#DCC40A', '#FFC800', '#F8A202', '#F17C04',
                    '#EA5505', '#E32F07', '#dc0909']
            },
            descriptions: {
                months: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
                weekdays: ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'],
                shortMonths: ['Янв', 'Фев', 'Март', 'Апр', 'Май', 'Июнь', 'Июль', 'Авг', 'Сент', 'Окт', 'Ноя', 'Дек'],
            },
            constants: {
                graph_types: ['line-graph', 'line'],
                day_graph_types: ['day-line-graph', 'day-line', 'day-graph'],
                heatmap_types: ['heatmap', 'symptom-heatmap'],
                report_types: ['report', 'formalized-report'],
            },
            axios: require('axios'),
            category_list: undefined,
            window_mode: window.MODE,
            object_id: window.OBJECT_ID,
            source: window.SOURCE,
            contract_id: window.CONTRACT_ID,
            is_admin: window.IS_ADMIN
        }
    }
})

window.onresize = function () {
    Event.fire('window-resized')
}

Vue.use(vmodal, {componentName: 'Modal'})
Vue.use(VueConfirmDialog)
Vue.use(VueEllipseProgress)
Vue.component('vue-confirm-dialog', VueConfirmDialog.default)
Vue.component('vue-ellipse-progress', VueEllipseProgress.default)

new Vue({
    render: h => h(App),
}).$mount('#app')
