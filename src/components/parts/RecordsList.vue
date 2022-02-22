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
          <colgroup>
            <col span="1" style="width: 40%;">
            <col span="1" style="width: 60%;">
          </colgroup>

          <tr class="table-info">
            <th colspan="2">{{ date.date }}</th>
          </tr>

          <tr v-for="record in date.records">
            <th>
              {{ record.category_info.description }}<br>
              <small class="text-muted">{{ record.formatted_date }}</small>
            </th>
            <td>
              <a href="#" v-if="record.category_info.type == 'file'" @click="downloadFile(record.attached_files[0])">{{ record.value }}</a>
              <span v-else>{{ record.value }}</span> {{ record.category_info.unit ? ` (${record.category_info.unit})` : '' }}
              {{
                record.category_info.name == 'medicine' && record.params && record.params.dose ? ` (${record.params.dose})` : ''
              }}
              <div v-if="record.params && record.params.comment">
                <strong>Комментарий: </strong> {{ record.params.comment }}
              </div>
              <br>
              <more-info-block title="Комментарии агентов" :id="'additions' + record.id" v-if="record.additions">
                <ul>
                  <li v-for="addition in record.additions" class="text-muted" style="font-size: small">
                    <span v-html="addition.addition.comment"/>{{ addition }}
                  </li>
                </ul>
              </more-info-block>
              <more-info-block title="Результаты по группам" :id="'group_results' + record.id"
                               v-if="record.params && record.params.group_scores  && !to_export">
                <ul>
                  <li v-for="(score, group) in record.params.group_scores" class="text-muted" style="font-size: small">
                    <strong>{{ group }}:</strong> {{ score }}
                  </li>
                </ul>
              </more-info-block>
              <more-info-block title="Технические параметры" :id="'params' + record.id"
                               v-if="record.params && !to_export">
                <span class="text-muted" style="font-size: small">{{ record.params }}</span>
              </more-info-block>

              <div class="text-muted" v-if="record.params && record.params.group_scores && to_export">
                <h6>Результаты по группам:</h6>
                <ul>
                  <li v-for="(score, group) in record.params.group_scores" class="text-muted" style="font-size: small">
                    <strong>{{ group }}:</strong> {{ score }}
                  </li>
                </ul>
              </div>

              <div class="text-muted" v-if="to_export && record.additions">
                <h6>Комментарии агентов:</h6>
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
import downloadjs from "downloadjs";

export default {
  name: "RecordsList",
  components: {MoreInfoBlock},
  props: ['data', 'to_export'],
  methods: {
    downloadFile: function (file) {
      this.axios.post(this.url('/api/settings/get_file'), file).then(response => {
        downloadjs(`data:${file.type};base64,${response.data.base64}`, file.name, file.type);
      }).catch(() => Event.fire('load-error'));
    }
  }
}
</script>

<style scoped>
h1, h2 {
  font-weight: normal;
}

body {
  background-color: #f8f8fb;
}

table tr {
  break-inside: avoid;
}

</style>