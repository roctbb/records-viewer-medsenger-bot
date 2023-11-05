<template>
  <div class="interactive-map" v-if="map">
    <human-map v-if="map == 'human'" :parts="parts" :id="id"/>
    <child-map v-if="map == 'child'" :parts="parts" :id="id"/>
  </div>
</template>

<script>

import HumanMap from "../../../maps/HumanMap.vue";
import ChildMap from "../../../maps/ChildMap.vue";

export default {
  name: "InteractiveMap",
  components: {HumanMap, ChildMap},
  props: ['map', 'parts', 'id']
}
</script>

<style>
#info-box {
  display: none;
  position: absolute;
  top: 0px;
  left: 0px;
  z-index: 1;
  background-color: #ffffff;
  border: 2px solid #006c88;
  border-radius: 5px;
  padding: 5px;
}
</style>
