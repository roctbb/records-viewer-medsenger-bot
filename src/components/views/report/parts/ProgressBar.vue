<template>
    <div class="progress" style="height: 15px;">
        <div class="progress-bar" role="progressbar"
             :style="get_part_style()"
             :aria-valuenow="value"
             :aria-valuemin="min" :aria-valuemax="max">
        </div>
    </div>
</template>

<script>
export default {
    name: "ProgressBar",
    components: {},
    props: {
        value: {
            required: true
        },
        color: {
            required: true
        },
        min: {
            required: true
        },
        max: {
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
        get_part_style: function () {
            let range = Math.abs(this.max  - this.min)
            return `width: ${100 * ((this.value - this.min) / range)}%;
                    background-color: ${this.color_transparency(this.color, 80)};
                    color: black`
        }
    },
    computed: {
        categories() {
            return this.field.bars
                .filter((part) => ['category'].includes(part.code))
                .map((part) => part.category)
        },
        record_groups() {
            if (!this.field.record_groups) return []

            return this.filter_groups(this.data.data.records, this.categories, this.field.group_filters)
        }
    }
}
</script>

<style scoped>

</style>