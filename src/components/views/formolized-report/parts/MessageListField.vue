<template>
    <div v-if="field">
        <loading v-if="!options.loaded"/>
        <div v-else>
            <div class="alert alert-success" role="alert"
                 v-if="!groups.length">
                {{ field.nothing_found_message }}
            </div>

            <div v-else>
                <div class="row">
                    <div class="col-6" v-for="(group, i) in groups" :key="'group_' + i">
                        <card :image="field.card_image ? images[field.card_image] : undefined" :big="true"
                              additional_style="display: block; padding: 10px; background-color: rgb(145,225,230,0.05);">
                            <div v-for="part in field.message_parts">
                                <!-- TITLE -->
                                <h6 class="text-center" v-if="part.code == 'title'">
                                    {{ get_title(part, group) }}
                                </h6>

                                <!-- DATE -->
                                <small v-if="part.code == 'date'">
                                    <i><b>{{ group.formatted_date }}</b> в {{ group.formatted_time }}</i>
                                    <br>
                                </small>

                                <!-- RECORDS -->
                                <div v-if="part.code == 'records_list'">
                                    <ul>
                                        <li v-for="record in group.records_by_categories[part.category]">{{ record.value }}</li>
                                    </ul>
                                </div>

                                <!-- TEXT -->
                                <div v-if="part.code == 'text'">
                                    <p v-for="record in group.records_by_categories[part.category]">{{ record.value }}</p>
                                </div>

                                <!-- MEDICINE -->
                                <div v-if="part.code == 'medicine_description'">
                                    <div v-for="medicine in group.records_by_categories[part.category]">
                                        <h6>{{ medicine.title }}</h6>
                                        <span v-if="medicine.dose"><strong>Дозировка: </strong>{{ medicine.dose }}<br></span>
                                        <span v-if="medicine.rules"><strong>Правила приема: </strong>{{ medicine.rules }}<br></span>
                                    </div>
                                </div>

                                <div class="text-center" v-if="part.code == 'compliance'">
                                    <vue-ellipse-progress :progress="get_compliance_percent(group)"
                                                          :color="get_compliance_color(group)"
                                                          :size="100" thickness="12"/>
                                </div>

                            </div>
                        </card>
                    </div>

                </div>
            </div>

        </div>
    </div>
</template>

<script>

import Loading from "../../../common/Loading.vue";
import Card from "../../../common/Card.vue";

export default {
    name: "MessageListField",
    components: {Card, Loading},
    props: {
        field: {
            required: true
        },
        data: {
            required: true
        }
    },
    data() {
        return {
            options: {
                loaded: false
            }
        }
    },
    created() {
        this.options.loaded = true
    },
    methods: {
        get_title: function (part,  group) {
            let title = part.text
            if (group.records[0].title)
                title = title.replace('@title', group.records[0].title)
            return title

        },
        get_compliance_percent: function (group) {
            return (group.records[0].done / group.records[0].requested * 100).toFixed(1) * 1
        },
        get_compliance_color: function (group) {
            return this.get_compliance_percent(group) > 50 ? this.colors.green : this.colors.red
        },
    },
    computed: {
        categories() {
            return this.field.message_parts
                .map((part) => part.category)
                .filter((part) => part)
        },
        groups() {
            let data = undefined

            if (this.field.record_groups)
                data = this.data.data.records
            if (this.field.prescription_groups)
                data = this.data.data.prescriptions
            if (this.field.compliance_groups)
                data = this.data.stats.compliance


            return data ? this.filter_groups(data, this.categories, this.field.group_filters) : []
        }
    }
}
</script>

<style scoped>
.row {
    margin-left: 0;
    margin-right: 0;
    column-gap: 0;
}

.alert {
    height: 100%;
    margin-bottom: 5px;
}

ul {
    margin-bottom: 0;
    padding-inline-start: 20px;
}
</style>