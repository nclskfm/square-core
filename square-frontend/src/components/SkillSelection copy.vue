<!-- The Navigation Bar at the top of the page. Most views should be reachable through this. -->
<template>
    <div class="center-block bg-light border rounded shadow p-3" style="border-bottom-style: solid;border-bottom-width: 0px;margin-bottom: 24px;">
        <div class="mb-3">
          <label for="skill1" class="form-label d-block placeholder-glow">
            <h1>1. Select a Skill</h1>
          </label>
  
          <div>
            <input v-model="searchText" placeholder="Search skill" class="search-bar form-control-lg mb-2" style="margin-left: 8px;" />
          </div>
          <div class="container" style="height: 20em; overflow-y: scroll;">
            <div class="row row-cols-1 row-cols-sm-2 row-cols-md-4 align-items-center">
              <div v-for="(skill, index) in filteredSkills" :key="skill.id">   
                <div class="col d-flex justify-content-center"> 
                  <input class="btn-check w-100 overflow-ellipsis" type="checkbox"
                      v-on:input="selectSkill(skill.id, index)"
                      v-bind:value="skill.id"
                      v-model="sel_list[index]"
                      :disabled="waiting"
                      :id="skill.id">
                  <label class="btn btn-outline-primary" :for="skill.id">
                    <h4> 
                      {{skill.name}}
                    </h4>
                    <div class="text-gray-400 text-sm">
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16">
                        <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
                        <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/>
                      </svg>
                      {{skill.skill_type}}
                      <span class="px-1.5 text-gray-300">• </span>
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-box-seam" viewBox="0 0 16 16">
                        <path d="M8.186 1.113a.5.5 0 0 0-.372 0L1.846 3.5l2.404.961L10.404 2l-2.218-.887zm3.564 1.426L5.596 5 8 5.961 14.154 3.5l-2.404-.961zm3.25 1.7-6.5 2.6v7.922l6.5-2.6V4.24zM7.5 14.762V6.838L1 4.239v7.923l6.5 2.6zM7.443.184a1.5 1.5 0 0 1 1.114 0l7.129 2.852A.5.5 0 0 1 16 3.5v8.662a1 1 0 0 1-.629.928l-7.185 2.874a.5.5 0 0 1-.372 0L.63 13.09a1 1 0 0 1-.63-.928V3.5a.5.5 0 0 1 .314-.464L7.443.184z"/>
                      </svg>
                      <!-- {{skill.default_skill_args.base_model}} -->
                    </div>
  
                  </label>
                    
                </div>
              </div>
            </div>
          </div>
          
      </div>
    </div>
  </template>
  
  <script>
  import Vue from 'vue'
  // import SkillSelector from '@/components/SkillSelector.vue'
  
  export default Vue.component('skill-selector', {
    props: ['selectorTarget', 'skillFilter'],
    data() {
      return {
        searchText: '',
        waiting: false,
        options: {
          selectedSkills: []
        },
        sel_list: [],
        chosenSkillType: ''
      }
    },
    components: {
      // SkillSelector
    },
    computed: {
      filteredSkills() {
        return this.searchText
          ? this.filteredSkills1.filter((item) => this.searchText
              .toLowerCase()
              .split(" ")
              .every(v => item.name.toLowerCase().includes(v)))
          : this.filteredSkills1
      },
      filteredSkills1() {
        if(this.chosenSkillType != ''){
          return this.availableSkills.filter(skill => skill.skill_type == this.chosenSkillType)}
        else{
          return this.availableSkills
        }
      },
      availableSkills() {
        let availableSkills = this.$store.state.availableSkills
        // Apply optional filter from props
        if (this.skillFilter !== undefined) {
          return availableSkills.filter(skill => this.skillFilter(skill.id))
        } else {
          return availableSkills
        }
      },
      availableSkillsBasedOnSettings() {
        return this.availableSkills.filter(skill => skill.skill_type === this.skillSettings.skillType
            && skill.skill_settings.requires_context === this.skillSettings.requiresContext)
      },
      selectedSkills() {
        return this.options.selectedSkills.filter(skill => skill !== 'None')
      },
      skillSettings() {
        let settings = {
          skillType: null,
          requiresContext: false,
          requiresMultipleChoices: 0
        }
        this.selectedSkills.forEach((skillId, index) => {
          this.availableSkills.forEach(skill => {
            if (skillId === skill.id) {
              if (index === 0) {
                settings.skillType = skill.skill_type
                settings.requiresContext = skill.skill_settings.requires_context
              } else if (skill.skill_type !== settings.skillType || skill.skill_settings.requires_context !== settings.requiresContext) {
                this.options.selectedSkills[index] = 'None'
              }
              // Require a minimum of 1 line if context is required else pick from the maximum of selected skills
              settings.requiresMultipleChoices = Math.max(
                  settings.requiresContext ? 1 : 0,
                  settings.requiresMultipleChoices,
                  skill.skill_settings.requires_multiple_choices)
            }
          })
        })
        return settings
      }
    },
    methods: {
      minSkillsSelected(num) {
        return this.selectedSkills.length >= num
      },
      selectSkill(skill_id, index) {
        if(this.sel_list[index] == true){
          this.$set(this.options.selectedSkills, index, "None")
        }
        else{
          this.$set(this.options.selectedSkills, index, skill_id)
        }
        this.$store.dispatch('selectSkill', { skillOptions: this.options, selectorTarget: this.selectorTarget })
        this.$emit('input', this.options, this.skillSettings)
  
        var empty = true;
        console.log(empty)
        console.log(this.sel_list.length)
        for(var i = 0; i<this.sel_list.length; i++){
          console.log("start list")
          console.log(i)
            if(this.sel_list[i] == true){
              empty=false;
  
          }
        }
        if(empty){
          this.chosenSkillType = this.availableSkills[index].skill_type
        }
        else{
          this.chosenSkillType = ''
        }
      },
  
      check_checkbox: function (index){
        this.sel_list[index] = true
      }
    },
    beforeMount() {
      this.waiting = true
      this.$store.dispatch('updateSkills')
          .then(() => {
            this.$store.state.skillOptions[this.selectorTarget].selectedSkills.forEach((skill, index) => {
              this.$set(this.options.selectedSkills, index, skill)
            })
            this.$emit('input', this.options, this.skillSettings)
          }).finally(() => {
            this.waiting = false
          })
    },
    mounted(){
      // while(this.sel_list.length<=this.availableSkills.length){
      //   console.log(this.sel_list.length)
      //   console.log(this.availableSkills.length)
      //   this.sel_list.push("None")
      // }
    }
  })
  </script>
  
  <style>
    /* .text-transparent {
      --tw-text-opacity: 1;
      color: rgba(var(--bs-primary-rgb), var(--tw-text-opacity));
    }
    .px-1\.5 {
      padding-left: .375rem;
      padding-right: .375rem;
    } */
    .text-sm {
      font-size: .875rem;
      line-height: 1.25rem;
    }
    .text-gray-400 {
      --tw-text-opacity: 1;
      color: rgba(156,163,175,var(--tw-text-opacity));
    }
    .search-bar {
      border: 1px solid #ced4da !important;
      border-radius: 0.25rem !important;
    }
    .btn-block {
    line-height: 4;
    width: 30%;
    }
    .p-2 {
      padding: .5rem;
      padding-top: 0.5rem;
      padding-right: 0.5rem;
      padding-bottom: 0.5rem;
      padding-left: 0.5rem;
    }
    .btn-sm {
      padding: .25rem .5rem;
      font-size: .875rem;
      line-height: 1.5;
      border-radius: .2rem;
    }
  
  </style>