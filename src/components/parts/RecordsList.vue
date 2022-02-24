<template>
  <div v-if="data">
    <div v-if="!data.length">
      <p style="text-align: center"><img :src="images.nothing_found"/></p>

      <p style="text-align: center">
        <small>Ничего не найдено.</small>
      </p>
    </div>

    <div v-else>
      <div v-for="(date,i) in data">
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
              <span v-if="record.category_info.type != 'file'">{{ record.value }}</span>
              {{ record.category_info.unit ? ` (${record.category_info.unit})` : '' }}
              {{
                record.category_info.name == 'medicine' && record.params && record.params.dose ? ` (${record.params.dose})` : ''
              }}
              <div class="row" v-for="file in record.attached_files">
                <img :src="images.file" height="20"/>
                <a href="#" @click="get_file(file, 'download')">{{ file.name }} (скачать)</a>
                <more-info-block title="Просмотр" :id="`file_${i}_${record.id}_${file.id}`"
                                 v-if="file.type.includes('image')" class="col-12">
                  <loading v-if="!files_to_show[file.id]"/>
                  <img :src="`data:${file.type};base64,${files_to_show[file.id].base64}`"
                       :style="`max-width: ${img_width}px; max-height: ${img_height}px;`" v-else/>
                </more-info-block>
              </div>
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
import Loading from "./Loading";

export default {
  name: "RecordsList",
  components: {Loading, MoreInfoBlock},
  props: ['data', 'to_export'],
  data() {
    return {
      files_to_show: {}
    }
  },
  computed: {
    img_width() {
      return Math.floor(window.innerWidth * 0.6)
    },
    img_height() {
      return Math.floor(window.innerHeight * 0.6)
    }
  },
  methods: {
    get_file: function (file, action) {
      this.axios.post(this.url('/api/settings/get_file'), file).then(response => {
        if (action == 'download')
          downloadjs(`data:${file.type};base64,${response.data.base64}`, file.name, file.type);
        else if (action == 'show')
          this.files_to_show[file.id] = response.data
        this.$forceUpdate()
        console.log(this.files_to_show)
      }).catch(() => Event.fire('load-error'));
    }
  },
  created() {
    Event.listen('open-more-info', (id) => {
      if (id.includes('file')) {
        let ids = id.split('_').filter(p => p != 'file').map(p => parseInt(p))
        if (!this.files_to_show[ids[2]]) {
          let file = this.data[ids[0]].records.find(r => r.id == ids[1]).attached_files.find(f => f.id == ids[2])
          this.get_file(file, 'show')
        }
      }
    })
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

img {
  object-fit: contain;
  object-position: left top;
}
</style>