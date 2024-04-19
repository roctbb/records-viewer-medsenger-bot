<template>
    <div>
        <h5>{{ form.title }}</h5>
        <div class="alert alert-info-outline" v-for="block in blocks" style="margin-bottom: 10px">
            <div v-for="(field, i) in block" v-if="show_field(field)" style="margin-bottom: 5px">
                <h6 v-if="field.type == 'header' && field.text">{{ field.text }}</h6>
                <p v-html="br(field.description)" v-if="field.type == 'header' && field.description"></p>

                <div v-if="field.type != 'header'" :class="get_field_class(field)" :style="get_field_styles(field)">
                    <form-group57 :check="field.type == 'checkbox'"
                                  :title="field.text" :key="i"
                                  style="margin-bottom: 5px"
                                  :description="field.description">
                        <p v-if="['integer', 'float', 'text', 'textarea', 'time'].includes(field.type)" class="answer">
                            {{ answers[field.uid] }}
                        </p>

                        <div v-if="field.type == 'file'">
                            <file-downloader :show_img="true" :file_description="find_file_by_name(answers[field.uid])"/>
                        </div>

                        <div v-if="field.type == 'checkbox'" style="width: 100%;">
                            <img :src="images.unchecked" height="25" v-if="!answers[field.uid]"/>
                            <img :src="images.checked" height="25" v-if="answers[field.uid]"/>
                        </div>

                        <div v-if="field.type == 'radio'">
                            <p class="answer" v-if="field.params.variants[answers[field.uid]]">{{
                                    field.params.variants[answers[field.uid]].text
                                }}</p>
                        </div>

                        <div v-if="field.type == 'scale'">
                            <visual-analog-scale :params="field.params" :colors="field.params.colors">
                                <div class="row">
                                    <div class="col d-flex justify-content-center"
                                         v-for="(color, i) in field.params.colors">
                                        <img :src="images.checked" height="25"
                                             v-if="(field.params.reversed ? -1 : 1) * i + field.params.start_from == answers[field.uid]"/>
                                    </div>
                                </div>
                            </visual-analog-scale>
                        </div>

                        <div v-if="field.type == 'map'">
                            <interactive-map :map="field.params.map" :in_table="true"
                                             :parts="answers[field.uid]"
                                             :uid="field.uid"/>
                        </div>

                        <div v-if="field.type == 'date'">
                            <p class="answer">{{ format_date_string(answers[field.uid]) }}</p>
                        </div>

                        <div v-if="field.type == 'range'">
                            <progress-bar :max="field.params.max" :min="field.params.min" :color="colors.medsenger[0]" :value="answers[field.uid]"/>
                            <b>{{ answers[field.uid] }}</b>
                        </div>

                        <div v-if="field.type == 'medicine_list'">
                            <div class="row" v-if="!mobile">
                                <div class="col-9"><small style="padding-left: 25px">Препарат</small></div>
                                <div class="col-3"><small>Доза</small></div>
                            </div>

                            <div v-for="(medicine, j) in answers[field.uid]">

                                <div class="row" v-if="!mobile">
                                    <div class="col-9 row">
                                        <img :src="images.pills" height="20" style="margin-right: 5px"/>
                                        <span class="answer">{{ medicine.title }}</span>
                                    </div>
                                    <div class="col-3">
                                        <span class="text-muted">{{ medicine.dose }}</span>
                                    </div>
                                </div>

                                <div class="row" v-if="mobile" style="column-gap: 5px">
                                    <img :src="images.pills" height="20"/>
                                    <span class="answer">{{ medicine.title }}</span>
                                    <span class="text-muted">{{ medicine.dose }}</span>
                                </div>

                            </div>
                        </div>
                    </form-group57>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import FormGroup48 from "../../../common/FormGroup-4-8";
import ErrorBlock from "../../../common/ErrorBlock";
import DatePicker from 'vue2-datepicker';
import InteractiveMap from "../parts/InteractiveMap";
import VisualAnalogScale from "./VisualAnalogScale.vue";
import ProgressBar from "./ProgressBar.vue";
import FormGroup57 from "../../../common/FormGroup-5-7.vue";
import FileDownloader from "./FileDownloader.vue";

export default {
    name: "FormPresenter",
    components: {FileDownloader, FormGroup57, ProgressBar, VisualAnalogScale, InteractiveMap, FormGroup48, ErrorBlock, DatePicker},
    props: {
        data: {required: true},
        answers: {required: true},
        files: {required: false},
        record_id: {required: false}
    },
    data() {
        return {
            form: {},
            fill_time: new Date(),
            blocks: [],
            hexTokens: {
                C: {
                    pattern: /\.|\,/
                }
            }

        }
    },
    computed: {},
    methods: {
        find_file_by_name: function (name) {
            return this.files.find((f) => f.name == name)
        },
        find_field_by_descriptor: function (descriptor) {
            if (descriptor) {
                return this.form.fields.find(f => {
                    return descriptor.uid && descriptor.uid === f.uid ||
                        descriptor === f.uid
                })
            }
        },
        format_date_string: function (date) {
            let parts = date.split('-')
            return `${parts[2]}.${parts[1]}.${parts[0]}`
        },
        show_field: function (field) {
            if (this.answers[field.uid] == undefined && field.type == 'question') return false

            if (field.show_if) {
                let show_if_field = this.find_field_by_descriptor(field.show_if)

                if (this.answers[field.show_if] // галочка
                    || this.answers[field.show_if.uid] &&
                    (field.show_if.ans != undefined && this.answers[field.show_if.uid] === field.show_if.ans // вариант ответа
                        || field.show_if.group_index != undefined && show_if_field.params.zone_groups &&
                        show_if_field.params.zone_groups[field.show_if.group_index].zones.filter((z) => this.answers[field.show_if.uid].includes(z)).length)) { // зоны

                    return this.show_field(show_if_field)
                }
                return false
            }
            return true

        },
        get_level: function (field) {
            if (field && field.show_if) {
                field = this.find_field_by_descriptor(field.show_if)
                return 1 + this.get_level(field)
            }
            return 1;
        },
        get_field_class: function (field) {
            if (field.show_if) return 'alert alert-secondary-outline'
            return ''
        },
        get_field_styles: function (field) {
            if (!field.show_if) return ''
            let color = ""
            let lvl = this.get_level(field)
            const change = 10 * (lvl - 1);

            if (field.params.color) {
                color = "#" + field.params.color
            } else {
                color = `rgb(${255},${255 - change}, ${255 - change})`
            }

            return `background-color: ${this.color_transparency(color, 30)};` +
                `border-left-color: ${color};` +
                `margin-bottom: 5px !important;` +
                `padding-left: ${(lvl - 1) * 10}px !important;`
        },
        load_form: function (form) {
            if (form.fields === undefined) {
                return;
            }

            this.form = form
            this.blocks = []

            this.fill_time = new Date()

            let block = []

            this.form.fields.forEach((item) => {
                if (item.type == 'header' && (item.subtype == 'block' || !item.subtype) && block.length != 0) {
                    this.blocks.push(block)
                    block = []
                }

                block.push(item)
            })
            this.blocks.push(block)

            setTimeout(() => {
                if (window.document.querySelector('input.monitoring-input'))
                    window.document.querySelector('input.monitoring-input').focus()
            }, 300)
        }
    },
    created() {
        Event.listen('form-loaded', (data) => {
            if (this.record_id != data.record_id) return
            if (this.data && this.data != 'not-found') {
                this.load_form(data.form)
            }
        })
    },
    mounted() {
        this.fill_time = new Date(this.answers.timestamp * 1000)
    }
}
</script>

<style scoped>
h5 {
    margin-bottom: 15px;
}

input[type=radio] {
    /* Double-sized Checkboxes */
    -ms-transform: scale(1.4); /* IE */
    -moz-transform: scale(1.4); /* FF */
    -webkit-transform: scale(1.4); /* Safari and Chrome */
    -o-transform: scale(1.4); /* Opera */
    transform: scale(1.4);
    padding: 10px;
}

strong {
    size: 1.02rem !important;
}

.form-check-label {
    margin-left: 0.5rem;
}

.form-check {
    padding-left: 30px;
    margin-top: 15px;
    margin-bottom: 15px;
}

.answer {
    color: black;
    margin-bottom: 0
}
</style>
