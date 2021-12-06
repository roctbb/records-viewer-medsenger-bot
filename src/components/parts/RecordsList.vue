<template>
  <div v-if="data">
    <div v-if="!data.length">
      <p style="text-align: center"><img :src="images.nothing_found"/></p>

      <p style="text-align: center">
        <small>Ничего не найдено.</small>
      </p>
    </div>

    <div v-else>
      <div v-for="date in data">
        <table class="table table-hover table-striped fixed-columns">
          <tr class="table-info">
            <th colspan="2">{{ date.date }}</th>
          </tr>

          <tr v-for="record in date.records">
            <th>
              {{ record.category_info.description }}<br>
              <small class="text-muted">{{ record.formatted_date }}</small>
            </th>
            <td>{{ record.value }} {{ record.category_info.unit ? ` (${record.category_info.unit})` : '' }}
              <br>
              <more-info-block title="Комментарии" :id="'additions' + record.id" v-if="record.additions">
                <ul>
                  <li v-for="addition in record.additions" class="text-muted" style="font-size: small">
                    <span v-html="addition.addition.comment"/></li>
                </ul>
              </more-info-block>
              <more-info-block title="Технические параметры" :id="'params' + record.id" v-if="record.params && !to_export">
                <span class="text-muted" style="font-size: small">{{ record.params }}</span>
              </more-info-block>

              <div class="text-muted" v-if="to_export">
                <ul>
                  <li v-for="addition in record.additions" class="text-muted" style="font-size: small">
                    <span v-html="addition.addition.comment"/></li>
                </ul>
              </div>
            </td>
          </tr>

          <tr v-if="date.symptoms.lenght">
            <th>Симптомы</th>
            <td>
              <ul>
                <li v-for="symptom in date.symptoms">{{ symptom.category_info.description }}</li>
              </ul>
            </td>
          </tr>
        </table>
      </div>

    </div>

  </div>
</template>

<script>
import MoreInfoBlock from "./MoreInfoBlock";
export default {
  name: "RecordsList",
  components: {MoreInfoBlock},
  props: ['data', 'to_export']
}
</script>

<style scoped>
h1, h2 {
  font-weight: normal;
}

a {
  color: #42b983;
}

body {
  background-color: #f8f8fb;
}

table.fixed-columns th{
  width: 20%;
}

table.fixed-columns td{
  width: 80%;
}

table tr {
  break-inside: avoid;
}

</style>