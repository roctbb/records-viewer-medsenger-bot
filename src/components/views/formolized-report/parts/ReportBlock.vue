<template>
    <div v-if="block">
        <card :title="block.title" :big="true" additional_style="display: block">
            <div v-for="(field, i) in block.fields">
                <div v-if="!(to_export && field.hide_in_pdf)">
                    <header-field :field="field" v-if="field.type == 'header'"/>
                    <table-field :data="data" :field="field" v-else-if="field.type == 'table'"/>
                    <action-field :data="data" :field="field" v-else-if="field.type == 'action' && !to_export"/>
                    <message-list-field :data="data" :field="field" v-else-if="field.type == 'message_list'"/>
                    <progress-bars-field :data="data" :field="field" v-else-if="field.type == 'progress_bars'"/>
                    <report-status-field :data="data" :field="field" :statuses="report.statuses" v-else-if="field.type == 'report_status'"/>
                </div>
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
import ReportStatusField from "./ReportStatusField.vue";

export default {
    name: "ReportBlock",
    components: {ReportStatusField, ProgressBarsField, MessageListField, ActionField, TableField, HeaderField, FormGroup48, Card},
    props: {
        report: {required: true},
        block: {required: true},
        data: {required: true},
        to_export: {required: false}
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