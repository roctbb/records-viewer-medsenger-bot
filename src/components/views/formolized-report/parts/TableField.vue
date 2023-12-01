<template>
    <div v-if="field">
        <loading v-if="!options.loaded"/>
        <div v-else>
            <div class="alert alert-success" role="alert"
                 v-if="!record_groups.length && field.record_groups">
                {{ field.nothing_found_message }}
            </div>
            <table class="table table-hover" :class="mobile ? 'table-responsive' : ''" v-else>
                <!-- ШИРИНА СТОЛБЦОВ -->
                <colgroup v-if="!field.fixed_col_width">
                    <col span="1" style="width: 25%;">
                    <col span="1" :style="`width: ${75 / field.cols.length}%;`" v-for="col in field.cols">
                </colgroup>
                <colgroup v-else>
                    <col span="1" :style="`width: ${col.width}%;`" v-for="col in field.cols">
                </colgroup>

                <!-- ЗАГОЛОВКИ -->
                <thead v-if="field.show_header">
                <tr class="">
                    <th scope="col" v-for="col in field.cols">{{ col.text }}</th>
                </tr>
                </thead>

                <tbody>
                <tr v-for="row in field.rows" v-if="!field.record_groups">
                    <td style="padding-left: 0">{{ row.text }}</td>
                    <td v-for="col in field.cols" :style="get_cell_color(col)">

                        <!-- SIMPLE MOVING AVERAGE -->
                        <span v-if="col.code == 'sma'">
                        <i v-if="!data.stats.sma || !data.stats.sma[row.category]">Нет данных</i>
                        <b v-else>{{ data.stats.sma[row.category].value.toFixed(2) * 1 }}</b>
                        </span>
                        <span v-if="col.code == 'sma_credible'">
                            <i v-if="!data.stats.sma || !data.stats.sma[row.category]">Нет данных</i>
                            <b style="color: darkgreen" v-else-if="data.stats.sma[row.category].credible">Надежный показатель</b>
                            <span style="color: red" v-else>
                                <b>Ненадежный показатель</b>
                                <br>
                                <i>*Данные за {{ data.stats.sma[row.category].filled_days }} дн. из {{ data.period }}</i>
                            </span>
                        </span>

                        <!-- ZONES -->
                        <span v-if="col.code == 'zone_percent'">
                        <i v-if="!data.stats.zones[row.category]">Нет данных</i>
                        <span v-else>
                            <b>{{ data.stats.zones[row.category][col.zone_index]['percent'].toFixed(2) * 1 }}% </b>
                        </span>
                    </span>
                    </td>
                </tr>
                <tr v-for="group in record_groups" v-if="field.record_groups">
                    <td v-for="col in field.cols" :style="get_cell_color(col, group)">
                        <!-- DATE -->
                        <small v-if="col.code == 'date'">
                            <b>{{ group.formatted_date }}</b> в {{ group.formatted_time }}
                        </small>

                        <!-- CATEGORY -->
                        <div v-if="col.code == 'category'">
                            <ul v-if="col.all_values">
                                <li v-for="record in group.records_by_categories[col.category]"><b>{{ record.value }}</b></li>
                            </ul>
                            <b v-else>{{ group.records_by_categories[col.category][0].value }}</b>
                        </div>

                        <!-- COMMENTS -->
                        <div style="color: firebrick" v-if="col.code == 'algorithm_comments'">
                            <ul>
                                <li v-for="comment in group.comments"><span v-html="comment"/></li>
                            </ul>
                        </div>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script>

import Loading from "../../../common/Loading.vue";

export default {
    name: "TableField",
    components: {Loading},
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
        get_cell_color: function (col, group) {
            let style = `background-color: `
            if (col.color)
                return style + this.color_transparency(col.color, 30)

            if (col.code == 'category') {
                let record = group.records_by_categories[col.category] ? group.records_by_categories[col.category][0] : undefined

                if (record && this.field.cell_color_conditions['comments'] && record.comments.length)
                    return style + this.color_transparency('red', 30)

            }
            return ''
        }
    },
    computed: {
        categories() {
            if (this.field.record_groups) {
                return this.field.cols
                    .filter((col) => col.code == 'category')
                    .map((col) => col.category)
            } else {
                return this.field.rows
                    .map((row) => row.category)
            }
        },
        record_groups() {
            if (!this.field.record_groups) return []

            return this.filter_groups(this.data.data.records, this.categories, this.field.group_filters)
        }
    }
}
</script>

<style scoped>
.table {
    margin: 5px 0;
    table-layout: fixed;
    width: 100%;
    text-align: left;
}


table tr {
    break-inside: avoid;
}

ul {
    margin-bottom: 0;
    padding-inline-start: 20px;
}
</style>