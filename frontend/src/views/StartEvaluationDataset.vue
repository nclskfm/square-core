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
        options: ["squad", "quoref",]
        //{ label: "Dataset", city: "Dataset" },
        //{ label: "Dataset 2", city: "Dataset 2" },
        //{ label: "Dataset 3", city: "Dataset 3", $isDisabled: true }, -->

    };
  },
  mounted(){
      getDataSets(this.$store.getters.authenticationHeader())
      .then((response) => {
        console.log("dataset list: ", response.data);
        this.datasets = response.data
        this.datasets = [
          {
            "name": "squad",
            "skill-type": "extractive-qa",
            "metric": "squad",
            "mapping": {
              "id-column": "id",
              "question-column": "question",
              "context-column": "context",
              "answer-text-column": "answers.text"
            }
          }, {
            "name": "quoref",
            "skill-type": "extractive-qa",
            "metric": "squad",
            "mapping": {
              "id-column": "id",
              "question-column": "question",
              "context-column": "context",
              "answer-text-column": "answers.text"
            }
          }, {
            "name": "commonsense_qa",
            "skill-type":" multiple-choice",
            "metric": "exact_match",
            "mapping": {
              "id-column": "id",
              "question-column": "question",
              "choices-columns": ["choices.text"],
              "choices-key-mapping-column": "choices.label",
              "answer-index-column": "answerKey"
            }
          }, {
            "name": "cosmos_qa",
            "skill-type": "multiple-choice",
            "metric": "exact_match",
            "mapping":{
              "id-column": "id",
              "question-column": "question",
              "choices-columns": ["answer0", "answer1", "answer2", "answer3"],
              "choices-key-mapping-column": null,
              "answer-index-column": "label"
            }
          }
        ]
      })
          console.log("coretta: ", this.datasets);

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
