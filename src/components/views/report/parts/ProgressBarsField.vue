<template>
    <div v-if="field">
        <loading v-if="!options.loaded"/>
        <div v-else>
            <div v-for="(bar, i) in field.bars" :key="'bar_' + i">
                <div class="row" style="margin:  10px -5px">
                    <div class="col-md-3">
                        {{ bar.text }}
                    </div>
                    <div class="col-md-9">
                        <div class="progress" style="height: 30px;">
                            <div class="progress-bar" role="progressbar"
                                 :style="get_part_style(bar, part)"
                                 :aria-valuenow="data.stats.zones[bar.category][part.zone_index].percent"
                                 aria-valuemin="0" aria-valuemax="100"
                                 v-if="part.code == 'zone_percent' && data.stats.zones[bar.category]" v-for="part in field.parts">
                                <b>{{ data.stats.zones[bar.category][part.zone_index].percent.toFixed(0) * 1 }}%</b>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>

import Loading from "../../../common/Loading.vue";
import FormGroup48 from "../../../common/FormGroup-4-8.vue";

export default {
    name: "ProgressBarsField",
    components: {FormGroup48, Loading},
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
        get_part_style: function (bar, part) {
            return `width: ${this.data.stats.zones[bar.category][part.zone_index].percent}%;
                    background-color: ${this.color_transparency(part.color, 80)};
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