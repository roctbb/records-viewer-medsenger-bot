<template>
    <div v-if="field" style="margin-top: 15px; margin-bottom: 5px;">
        <div class="row" style="margin: -5px">
            <div class="col-md-5">
                <a class="btn btn-primary btn-block" target="_blank" :href="get_url" v-if="!field.params">{{ field.text }}</a>
                <button class="btn btn-primary btn-block" @click="send_request()" v-else>{{ field.text }}</button>
            </div>
            <div class="col-md-7" v-if="field.params">
                <div v-for="param in field.params">
                    <textarea class="form-control form-control-sm"
                              v-if="param.type == 'textarea'" v-model="request_data[param.code]"></textarea>
                    {{ param.description }}
                </div>
            </div>
        </div>
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
        return {
            request_data: {}
        }
    },
    created() {
    },
    computed: {
        get_url() {
            let paster = (S) => {
                return S.replace('@start_date', (this.data.dates[0].getTime()).toString())
                .replace('@end_date', (this.data.dates[1].getTime()).toString())
                .replace('@library_agent_id', `${window.AGENTS.LIBRARY_AGENT_ID}`)
                .replace('@cdss_agent_id', `${window.AGENTS.CDSS_AGENT_ID}`)
            }

            let action = paster(this.field.action)
            let agent = undefined

            if (this.field.agent) {
                agent = paster(this.field.agent)
            }

            return this.url(action, agent)
        },
    },
    methods: {
        send_request: function () {
            this.$confirm({
                message: `${this.field.text}?`,
                button: {
                    no: 'Нет',
                    yes: 'Да'
                },
                callback: confirm => {
                    if (confirm) {
                        this.axios
                            .post(this.get_url, this.request_data)
                            .then((response) => {
                                Event.fire('action-done')
                            })
                    }
                }
            })
        }
    }
}
</script>

<style scoped>
.row {
    grid-column-gap: 0;
}
</style>