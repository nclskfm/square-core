<template>
  <div>
    <multiselect
      id="dataset_evaluation"
      v-model="value"
      placeholder="Select the name of the dataset"
      :options="options"
      label="label"
      track-by="id"
      :custom-label="labelWithCity"
      :multiple="false"
      :clear-on-select="true"
      :close-on-select="true"
      :show-no-results="true"
      :hide-selected="false"
    >
      <!-- affichage du multiselect plié -->
      <template slot="singleLabel" slot-scope="{ option }">
        <strong>{{ option }}</strong>
        <!-- <span style="color: black">&nbsp;{{ option }}</span> -->
      </template>
      <!-- affichage des options(multiselect déplié) -->
      <template slot="option" slot-scope="{ option }">
        <div class="option__desc">
          <span class="option__title">
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
import { getDataSets } from '@/api'
export default {
  components: {
    Multiselect,
  },
  data() {
    return {
      value: null,
        datasets: [],
        options: []
        //{ label: "Dataset", city: "Dataset" },
        //{ label: "Dataset 2", city: "Dataset 2" },
        //{ label: "Dataset 3", city: "Dataset 3", $isDisabled: true }, -->
    };
  },
  mounted(){
      getDataSets(this.$store.getters.authenticationHeader())
      .then((response) => {
        for (let item_dataset = 0; item_dataset < response.data.length; item_dataset++){
        this.datasets.push(response.data[item_dataset].name);
        }
        this.options = this.datasets;
        console.log("datasets: ", this.options);
      })
      },
  methods: {
    //l'affichage des options lorsqu'il n'y a pas de template avec slot=singleLabel ou slot=option
    labelWithCity({ label, city }) {
      return `${label} — [${city}]`;
    },
    pushdataset(){
    }
  },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.min.css">
#dataset_select{
    width: fit-content;
}
</style>