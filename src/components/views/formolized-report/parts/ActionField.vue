<template>
    <div v-if="field" style="margin-top: 15px; margin-bottom: 5px;">
        <a class="btn btn-primary" target="_blank" :href="get_url">{{field.text}}</a>
    </div>
</template>

<script>

export default {
    name: "ActionField",
    components: {},
    props: {
        field: {
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
    computed: {
        get_url() {
            let action = this.field.action
                .replace('@start_date', (this.data.dates[0].getTime()).toString())
                .replace('@end_date', (this.data.dates[1].getTime()).toString())
                .replace('@library_agent_id', `@${window.AGENTS.LIBRARY_AGENT_ID}`)
                .replace('@cdss_agent_id', `@${window.AGENTS.CDSS_AGENT_ID}`)

            return this.url(action)
        },
    },
    methods: {}
}
</script>

<style scoped>

</style>