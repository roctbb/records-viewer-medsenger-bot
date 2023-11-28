<template>
    <div v-if="block">
        <card :title="block.title" :big="true" additional_style="display: block">
            <div v-for="(field, i) in block.fields">
                <header-field :field="field" v-if="field.type == 'header'"/>
                <table-field :data="data" :field="field" v-else-if="field.type == 'table'"/>
                <action-field :data="data" :field="field" v-else-if="field.type == 'action'"/>
                <message-list-field :data="data" :field="field" v-else-if="field.type == 'message_list'"/>
                <progress-bars-field :data="data" :field="field" v-else-if="field.type == 'progress_bars'"/>
            </div>
        </card>
    </div>
</template>

<script>
import Card from "../../../common/Card.vue";
import FormGroup48 from "../../../common/FormGroup-4-8.vue";
import HeaderField from "./HeaderField.vue";
import TableField from "./TableField.vue";
import ActionField from "./ActionField.vue";
import MessageListField from "./MessageListField.vue";
import ProgressBarsField from "./ProgressBarsField.vue";

export default {
    name: "ReportBlock",
    components: {ProgressBarsField, MessageListField, ActionField, TableField, HeaderField, FormGroup48, Card},
    props: {
        block: {
            required: true
        },
        data: {
            required: true
        }
    },
    data() {
        return {}
    },
    created() {
    },
    methods: {}
}
</script>

<style scoped>
.card-body {
    display: block !important;
    flex-flow: column;
    justify-content: space-between;
    align-items: start;
}
</style>