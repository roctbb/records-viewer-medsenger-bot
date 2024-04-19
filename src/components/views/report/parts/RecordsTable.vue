<template>
    <div>
        <div v-for="(info, date) in records.by_dates">
            <table :class="`table table-hover ${info.last_date ? 'last-table' : ''}`">
                <colgroup>
                    <col span="1" style="width: 10%;">
                    <col span="1" style="width: 30%;">
                    <col span="1" style="width: 60%;">
                </colgroup>

                <thead>
                <tr>
                    <th colspan="5">{{ date }}</th>
                </tr>
                </thead>

                <tbody>
                <!-- свернутые записи -->
                <tr v-for="category in options.text_categories" v-if="info[category.code].length">
                    <td></td>
                    <!-- категория -->
                    <td>
                        <b>{{ category.description }}</b>
                    </td>
                    <!-- значения -->
                    <td>
                        <span v-for="record in info[category.code]">
                            <span class="text-muted">{{ record.formatted_time }}</span> –
                            <span :style="record.warnings ? ('color: ' + colors.red[0]) : '' ">{{ record.value }} </span><br>
                        </span>
                    </td>
                </tr>

                <!-- все записи -->
                <tr v-for="record in info.all_records">
                    <!-- время -->
                    <td class="time-cell" v-if="!mobile"><span class="text-muted">{{ record.formatted_time }}</span></td>
                    <!-- категория -->
                    <td :colspan="mobile? 2 : 1">
                        <span class="text-muted" v-if="mobile">{{ record.formatted_time }}<br></span>
                        <b>{{ record.category_info.description }}</b>
                    </td>

                    <!-- значение -->
                    <td>
                        <span>{{ record.value }}</span>

                        <!-- Файлы -->
                        <div v-for="file in record.attached_files" v-if="record.category_code != 'action'">
                            <file-downloader :show_img="to_export" :file_description="file"/>
                        </div>

                        <!-- Комментарии -->
                        <div v-if="record.comment">
                            <strong>Дополнительно: </strong> {{ record.comment }}
                        </div>

                        <!-- Предупреждения -->
                        <div class="alert alert-danger-outline" role="alert" v-if="record.warnings">
                            <b><u>Экстренные уведомления</u></b>
                            <ul>
                                <li v-for="(warning, i) in record.warnings"><span v-html="warning"/></li>
                            </ul>
                        </div>

                        <!-- Интегральная оценка -->
                        <div class="alert alert-info-outline" role="alert" v-if="record.group_scores">
                            <b><u>Результаты по группам</u></b>
                            <ul>
                                <li v-for="(score, group) in record.group_scores"><b>{{ group }}:</b> {{ score }}</li>
                            </ul>
                        </div>

                        <!-- Карта -->
                        <div v-if="record.map">
                            <br>
                            <interactive-map :map="record.map" :parts="record.params.answer" :id="record.id"/>
                        </div>

                        <!-- Настройки алгоритма -->
                        <div class="alert alert-info-outline" role="alert" v-if="record.algorithm_params">
                            <b><u>Настройки алгоритма</u></b>
                            <ul>
                                <li v-for="param in record.algorithm_params"><b>{{ param.name }}:</b> {{ param.value }}</li>
                            </ul>
                        </div>

                        <!-- Ответ на форму -->
                        <div v-if="record.params && record.params.form_answers">
                            <more-info-block title="Посмотреть ответы"
                                             :id="`form_answers_${record.id}_${record.params.form_id}`"
                                             v-if="!to_export">
                                <span class="text-muted" v-if="forms_to_show[record.params.form_id] == 'not-found'">Опросник не найден...</span>
                                <loading v-if="!forms_to_show[record.params.form_id] || forms_to_show[record.params.form_id] == 'loading'"/>
                                <form-presenter :data="forms_to_show[record.params.form_id]" :record_id="record.id"
                                                :answers="record.params.form_answers" :files="record.attached_files"/>
                            </more-info-block>

                            <div v-else>
                                <span class="text-muted" v-if="forms_to_show[record.params.form_id] == 'not-found'">Опросник не найден...</span>
                                <form-presenter :data="forms_to_show[record.params.form_id]"  :record_id="record.id"
                                                :answers="record.params.form_answers" :files="record.attached_files"/>
                            </div>
                        </div>

                        <!-- Технические параметры -->
                        <more-info-block title="Технические параметры" :id="'params' + record.id"
                                         v-show="record.params && is_admin && !to_export">
                            <span class="text-muted" style="font-size: small">{{ record.params }}</span>
                        </more-info-block>
                    </td>
                </tr>

                </tbody>
            </table>
        </div>
    </div>
</template>

<script>
import MoreInfoBlock from "./MoreInfoBlock.vue";
import downloadjs from "downloadjs";
import Loading from "../../../common/Loading.vue";
import InteractiveMap from "./InteractiveMap.vue";
import NothingFound from "../../../common/NothingFound.vue";
import moment from "moment/moment";
import FormPresenter from "./FormPresenter.vue";
import FileDownloader from "./FileDownloader.vue";

export default {
    name: "RecordsTable",
    components: {FileDownloader, FormPresenter, NothingFound, InteractiveMap, Loading, MoreInfoBlock},
    props: ['data', 'to_export'],
    data() {
        return {
            forms_to_show: {},
            options: {
                text_categories: [
                    {code: 'symptom', description: 'Симптомы'},
                    {code: 'side_effect', description: 'Побочные эффекты'}],
            },
            records: {
                all: undefined,
                by_dates: undefined
            }
        }
    },
    computed: {
    },
    methods: {
        process_records: function (records) {
            return records.map((record) => {
                let new_rec = {}
                this.copy(new_rec, record)
                if (new_rec.attached_files) {
                    if (new_rec.attached_files[0] && new_rec.value == new_rec.attached_files[0].name)
                        new_rec.value = "Загружен файл"
                }

                if (new_rec.params && new_rec.params.form_answers) {
                    if (!this.forms_to_show[new_rec.params.form_id]) {
                        this.forms_to_show[new_rec.params.form_id] = 'loading'
                        this.get_form(new_rec.params.form_id, new_rec.id)
                    }
                }

                if (new_rec.category_info.unit)
                    new_rec.value += `, ${new_rec.category_info.unit}`

                let warnings = this.comment_additions(new_rec).map((a) => a.addition.comment)
                if (warnings.length)
                    new_rec.warnings = warnings

                if (new_rec.params) {
                    if (new_rec.params.dose)
                        new_rec.value += ` (доза: ${new_rec.params.dose})`

                    if (new_rec.params.group_scores)
                        new_rec.group_scores = record.params.group_scores

                    if (new_rec.params.map)
                        new_rec.map = new_rec.params.map

                    if (new_rec.params.comment)
                        new_rec.comment = new_rec.params.comment

                    if (new_rec.params.algorithm_params && new_rec.params.algorithm_params.length)
                        new_rec.algorithm_params = new_rec.params.algorithm_params
                }

                return new_rec
            })
        },
        records_by_dates: function () {
            let all_records = this.records.all.sort((a, b) => b.timestamp - a.timestamp)
            let records_by_dates = this.group_by(all_records, 'formatted_date')
            let dates = {}

            let last_index = Object.entries(records_by_dates).length - 1
            let text_categories_codes = this.options.text_categories.map((c) => c.code)

            Object.entries(records_by_dates).forEach(([date, records], index) => {
                records = this.process_records(records)

                dates[date] = {
                    all_records: records
                        .filter((record) => !text_categories_codes.includes(record.category_code)),
                    last_date: index == last_index
                }

                text_categories_codes.forEach((c) => {
                    dates[date][c] = records
                        .filter((record) => record.category_code == c)
                })
            })

            return dates
        },
        get_form: function (form_id, record_id) {
            this.send_order('get_form', 'FORMS', {form_id: form_id, record_id: record_id}, 'form-loaded', false)
        }
    },
    mounted() {
        this.records.all = this.data
        if (this.records.all)
            this.records.by_dates = this.records_by_dates()

        Event.listen('refresh-records-table', (data) => {
            this.records.all = data
            this.records.by_dates = this.records_by_dates()
            this.$forceUpdate()
        })


        Event.listen('form-loaded', (data) => {
            this.forms_to_show[data.form.id] = data.form
            this.$forceUpdate()
        })

        Event.listen('open-more-info', (id) => {
            if (id.includes('form_answers')) {
                let ids = id.replace('form_answers_', '').split('_').map(p => parseInt(p))
                if (!this.forms_to_show[ids[1]]) this.get_form(ids[1], ids[0])
            }
        })

    }
}
</script>

<style scoped>
table {
    border-bottom: 0 !important;
    margin-bottom: 0;
}

.last-table {
    border-bottom: 3px solid #24a8b4 !important;
}

.time-cell {
//vertical-align: bottom;
}

img {
    object-fit: contain;
    object-position: left top;
}

.alert {
    margin-bottom: 0;
    margin-top: 5px;
}

ul {
    padding-left: 15px;
    margin-bottom: 0;
}
</style>