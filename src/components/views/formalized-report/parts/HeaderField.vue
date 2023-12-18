<template>
    <div v-if="field" style="margin-top: 15px; margin-bottom: 5px;">
        <h6><u>{{ field.text }}</u></h6>
    </div>
</template>

<script>

export default {
    name: "HeaderField",
    components: {},
    props: {
        field: {
            required: true
        }
    },
    data() {
        return {
        }
    },
    created() {
    },
    methods: {
    }
}
</script>

<style scoped>
h6 {
    font-size: 18px;
}
</style>