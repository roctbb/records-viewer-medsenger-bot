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
                        <div v-for="file in record.attached_files">
                            <span class="text-muted" v-if="files_to_show[file.id] == 'not-found'">Файл не найден...</span>
                            <div class="row" v-else-if="!to_export">
                                <img :src="images.file" height="20" style="margin-right: 5px"/>
                                <a href="#" @click="get_file(file, 'download')">{{ file.name }} (скачать)</a>
                            </div>

                            <div v-if="to_export && file.type.includes('image') && files_to_show[file.id] && files_to_show[file.id] != 'not-found'">
                                <img :src="`data:${file.type};base64,${files_to_show[file.id].base64}`"
                                     :style="`max-width: ${img_width}px; max-height: ${img_height}px;`"/>
                            </div>

                            <more-info-block title="Просмотр изображения" :id="`file_${record.id}_${file.id}`"
                                             v-if="!to_export && file.type.includes('image') && files_to_show[file.id] != 'not-found'">

                                <loading v-if="!files_to_show[file.id]"/>
                                <img :src="`data:${file.type};base64,${files_to_show[file.id].base64}`"
                                     :style="`max-width: ${img_width}px; max-height: ${img_height}px;`" v-else/>

                            </more-info-block>
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

                        <!-- Технические параметры -->
                        <more-info-block title="Технические параметры" :id="'params' + record.id"
                                         v-show="record.params && is_admin">
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

export default {
    name: "RecordsTable",
    components: {NothingFound, InteractiveMap, Loading, MoreInfoBlock},
    props: ['data', 'to_export'],
    data() {
        return {
            files_to_show: {},
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
        img_width() {
            if (this.to_export) return 500
            return Math.floor(window.innerWidth * (this.mobile ? 0.5 : 0.6))
        },
        img_height() {
            if (this.to_export) return 500
            return Math.floor(window.innerHeight * (this.mobile ? 0.5 : 0.6))
        }
    },
    methods: {
        process_records: function (records) {
            return records.map((record) => {
                let new_rec = {}
                this.copy(new_rec, record)
                if (new_rec.attached_files) {
                    if (new_rec.attached_files[0] && new_rec.value == new_rec.attached_files[0].name)
                        new_rec.value = "Загружен файл"
                    new_rec.attached_files.forEach((file) => {
                        if (file.type.includes('image'))
                            this.get_file(file, 'show', false)
                    })
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
            }).sort((a, b) => a.timestamp - b.timestamp)
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

        get_file: function (file, action, show_error=true) {
            this.axios
                .get(this.direct_url('/api/get_file/' + file.id))
                .then(response => {
                    if (action == 'download')
                        downloadjs(`data:${file.type};base64,${response.data.base64}`, file.name, file.type);
                    else if (action == 'show')
                        this.files_to_show[file.id] = response.data
                    this.$forceUpdate()
                })
                .catch((e) => {
                    this.files_to_show[file.id] = 'not-found'
                    this.$forceUpdate()
                    if (show_error) Event.fire('load-error')
                });
        },
        load_images: function () {

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

        Event.listen('file-not-found', (id) => {
            this.files_to_show[id] = 'not-found'
        })

        Event.listen('open-more-info', (id) => {
            if (id.includes('file')) {
                let ids = id.split('_').filter(p => p != 'file').map(p => parseInt(p))
                if (!this.files_to_show[ids[1]]) {
                    let file = this.records.all.find(r => r.id == ids[0]).attached_files.find(f => f.id == ids[1])
                    this.get_file(file, 'show')
                }
            }
        })

        // Загрузка файла
        Event.listen('generate-report', () => {
            this.load_images()
        });

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