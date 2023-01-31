<template>
  <div>
    <multiselect
      id="metric_evaluation"
      v-model="value"
      value="item"
      :options="metrics"
      placeholder="Select the name of metric"
      label="name"
      track-by="id"
      :custom-label="labelWithCity"
      :multiple="false"
      :clear-on-select="true"
      :close-on-select="true"
      :show-no-results="true"
      :hide-selected="false"
      :allow-empty="true"
            @select="optionSelected">


      <!-- affichage du multiselect plié -->
      <template slot="singleLabel" slot-scope="{ option }">
        <strong>{{ option }}</strong>
        <!-- <span style="color: red">&nbsp;{{ option}}</span> -->
      </template>
      <!-- affichage des options(multiselect déplié) -->
      <template slot="option" slot-scope="{ option }">
        <div class="option__desc">
          <span class="option__title" >
            <strong>{{ option }}&nbsp;</strong>
          </span>
          <!-- <span class="option__small" style="color: green">{{
            option
          }}</span> -->
        </div>
      </template>
    </multiselect>
  </div>
</template>
<script>
import Multiselect from "vue-multiselect";

export default {
  components: {
    Multiselect,
  },

  data() {
    return {
          item: {
        name: 'Not selected'
      },
      value: null,
      metrics: ["squad", "squad_v2", "exact_match"],
    };
  },
   computed: {

  },

  methods: {
    //l'affichage des options lorsqu'il n'y a pas de template avec slot=singleLabel ou slot=option
    labelWithCity({ label, city }) {
      return `${label} — [${city}]`;
    },
        onSelect(option) {
      this.item = option
    }
  },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
