<template>
  <div id="app">
  <div>Evaluation</div>
  <div></div>
  <p style="display: none;">Please select the skill, Dataset and Metric to make a new evaluation</p>

  <div id="skill_block">
    <label>Skill</label>

    <EvaluationSkill  />
  </div>

    <div id="dataset_block">
    <label >Dataset</label>

    <EvaluationDataset msg="Hello Vue in CodeSandbox!" />
  </div>

    <div id="dataset_block">
    <label >Metric</label>

    <EvaluationMetric msg="Hello Vue in CodeSandbox!" />
  </div>
  <div>
      <router-link class='btn btn-primary' to='/leaderboard' exact-active-class='active'>Start Evaluation</router-link>
    </div>
  </div>
</template>

<script>
import EvaluationSkill from "/src/views/StartEvaluationSkill";
import EvaluationDataset from "/src/views/StartEvaluationDataset";
import EvaluationMetric from "/src/views/StartEvaluationMetric";

export default {
  name: "App",
  components: {
    EvaluationSkill,
    EvaluationDataset,
    EvaluationMetric
  },
};
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left;
  color: #2c3e50;
}
</style>
