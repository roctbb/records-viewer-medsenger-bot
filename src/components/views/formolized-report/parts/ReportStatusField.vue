<template>
    <div v-if="field">
        <loading v-if="!options.loaded"/>
        <div v-else>
            <card v-if="report_status" :image="images[report_status.icon]" :big="true"
                  :additional_style="`display: block; padding: 10px; background-color: ${color_transparency(report_status.color, 10)}`">
                <!-- TITLE -->
                <h6>{{ report_status.title }}</h6>

                <!-- TEXT -->
                <span v-html="description"/>

                <!-- COMMENTS -->
                <div v-if="report_status.comments">
                    <ul>
                        <li v-for="comment in report_status.comments"><span v-html="comment"/></li>
                    </ul>
                </div>
            </card>
        </div>
    </div>
</template>

<script>

import Loading from "../../../common/Loading.vue";
import Card from "../../../common/Card.vue";

export default {
    name: "ReportStatusField",
    components: {Card, Loading},
    props: {
        statuses: {required: true},
        field: {required: true},
        data: {required: true}
    },
    data() {
        return {
            options: {
                loaded: false
            },
            report_status: {
                comments: []
            }
        }
    },
    created() {
        this.options.loaded = false
        this.report_status = undefined
        let comments = []

        this.statuses.forEach((report_status) => {
            if (this.report_status) return
            report_status.rules.forEach((rule) => {
                let stats = this.data.stats[rule.code]

                rule.conditions.forEach((condition) => {
                    let value = stats[condition.category].value
                    let condition_eval = condition.condition.replaceAll('@value', value)
                    let comment = condition.description.replaceAll('@value', value)

                    condition.params.forEach((p) => {
                        comment = comment.replaceAll('@' + p, this.data.params[p].value)
                        condition_eval = condition_eval.replaceAll('@' + p, this.data.params[p].value)
                    })

                    if (eval(condition_eval)) comments.push(comment)
                })
            })

            if (comments.length) {
                this.report_status = report_status
                this.report_status.comments = comments
            }
        })

        this.options.loaded = true
    },
    methods: {},
    computed: {
        description: function () {
            if (!this.report_status.description) return ''

            let description = this.report_status.description

            Object.entries(this.data.params).forEach(([param, options]) => {
                description = description.replace('@' + param, options.value)
            })

            return description
        }
    }
}
</script>

<style scoped>
ul {
    margin-bottom: 0;
    padding-inline-start: 20px;
}
</style>