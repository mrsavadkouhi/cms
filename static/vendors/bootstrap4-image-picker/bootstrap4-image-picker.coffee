# Bootstrap 4 Image Picker
# By Mohammad Amir Heshmatkhah
# maheshmatkhah.prg@gmail.gom
# Forked from https://github.com/rvera/image-picker
#
# MIT License, https://github.com/rvera/image-picker/blob/master/LICENSE
#
# You have to import this after jQuery
# Styling system is based on Bootstrap v4 and font-awesome v5
#
#

jQuery.fn.extend({
  bs4ImagePicker: (opts = {}) ->
    this.each () ->
      select = jQuery(this)
      select.data("picker").destroy() if select.data("picker")
      select.data("picker", new Bootstrap4ImagePicker(this, sanitized_options(opts)))
      opts.initialized.call(select.data("picker")) if opts.initialized?
})

sanitized_options = (opts) ->
  default_options = {
    hide_select: true,
    show_label: false,
    limit: undefined, # will overwrite with data-limit
    initialized: undefined, # function(imagePicker){...}
    changed: undefined, # function(select, newValues, oldValues, event){...}
    clicked: undefined, # click_handler function(select, picker option, event){...}
    selected: undefined, # function(select, picker option, event){...}
    limit_reached: undefined, # function(select){...}
    search_handler: undefined, # function(pickerObj, options){...}
    tooltip_options: {
      placement: 'bottom',
      title: 'Click to Clear'
    }
    template: {
      wrapper: "<div class='image-picker p-2 m-2 border'>",
      control_wrapper: "<div class='row border controls'>",
      list_wrapper: "<div class='row border grid'>",
      search: "<div class='col-12 m-2 inner-addon right-addon'><i class='fa fa-search'></i><input type='text' class='form-control' placeholder='Search for option ...'></div>",
      detail_label: "<div class='col-2 text-center cursor-default m-2 d-inline' data-toggle='tooltip'><span class='badge badge-info'></span> Selected</div>",
      filter_label: "<div class='col-2 text-center cursor-default m-2 d-inline'>Showing <span class='badge badge-warning'></span></div>",
      filter_clear: "<div class='col-2 mb-2'><div class='btn btn-rounded btn-block btn-sm btn-outline-warning'>Clear Filter</div></div>",
      filter_selected_only: "<div class='col-2 mb-2'><div class='btn btn-rounded btn-block btn-sm btn-outline-success'>Show Selected Items</div></div>",
      filter_unselected_only: "<div class='col-2 mb-2'><div class='btn btn-rounded btn-block btn-sm btn-outline-primary'>Show Unselected Items</div></div>",
      group_wrapper: "<div class='col-12 row'>",
      group_title: "<h2 class='font-bold'>",
      item: "<div class='grid-item my-2 col-lg-3 col-md-4 col-sm-6 col-xs-12'>
              <div class='card'>
                <content/>
              </div>
				   </div>",
      image: "<img class='card-img-top'>",
      label: "<div class='card-body'>
                <h3 class='text-center card-title'><content/></h3>
              </div>",
      check: "<i class='fa fa-4x fa-check check-mark' style='position: absolute;'></i>"
    }

  }
  jQuery.extend(default_options, opts)

both_array_are_equal = (a, b) ->
  return false if (!a || !b) || (a.length != b.length)
  a = a[..]
  b = b[..]
  a.sort()
  b.sort()
  for x, i in a
    return false if b[i] != x
  true

class Bootstrap4ImagePicker
  constructor: (select_element, @options = {}) ->
    @select_element = jQuery(select_element)
    @multiple = @select_element.attr("multiple") == "multiple"
    @options.limit = parseInt(@select_element.data("limit")) if @select_element.data("limit")?
    @build_and_append_picker()

  destroy: ->
    for option in @picker_options
      option.destroy()
    @picker.remove()
    @select_element.off("change", @sync_picker_with_select)
    @select_element.removeData "picker"
    @select_element.show()

  build_and_append_picker: () ->
    @select_element.hide() if @options.hide_select
    @select_element.on("change", @sync_picker_with_select)
    @picker.remove() if @picker?
    @create_picker()
    @select_element.after(@picker)
    @sync_picker_with_select()

  sync_picker_with_select: () =>
    for option in @picker_options
      if option.is_selected()
        option.mark_as_selected()
      else
        option.unmark_as_selected()
    @details.update_details()

  create_picker: () ->
    @picker_options = []

    @picker = jQuery(@options.template.wrapper)

    @picker_control = jQuery(@options.template.control_wrapper)
    @picker_list = jQuery(@options.template.list_wrapper)

    @picker.append(@picker_control)
    @picker.append(@picker_list)

    # create search element
    @search = new Bootstrap4ImagePickerSearchBar(this, @options)
    @picker_control.append(@search.element)

    # create details panel
    @details = new Bootstrap4ImagePickerDetailPanel(this, @options, @picker_control)
    #		@picker_control.append(@details.element)

    @recursively_parse_option_groups(@select_element, @picker_list)
    @picker

  recursively_parse_option_groups: (scoped_dom, target_container) ->
    for option_group in scoped_dom.children("optgroup")
      option_group = jQuery(option_group)
      container = jQuery(@options.template.group_wrapper)
      container.append(jQuery(@options.template.group_title).append(option_group.attr("label")))
      target_container.append(container)
      @recursively_parse_option_groups(option_group, container)
    for option in (new Bootstrap4ImagePickerOption(option, this, @options) for option in scoped_dom.children("option"))
      @picker_options.push option
      continue if !option.has_image()
      target_container.append option.node


  has_implicit_blanks: () ->
    (option for option in @picker_options when (option.is_blank() && !option.has_image())).length > 0

  selected_values: () ->
    if @multiple
      @select_element.val() || []
    else
      [@select_element.val()]

  toggle: (imagepicker_option, original_event) ->
    old_values = @selected_values()
    selected_value = imagepicker_option.value().toString()
    if @multiple
# deselect if selected
      if selected_value in @selected_values()
        new_values = @selected_values()
        new_values.splice(jQuery.inArray(selected_value, old_values), 1)
        @select_element.val []
        @select_element.val new_values
      else
        if @options.limit? && @selected_values().length >= @options.limit
          if @options.limit_reached?
            @options.limit_reached.call(@select_element)
        else
          @select_element.val @selected_values().concat selected_value
    else
      if @has_implicit_blanks() && imagepicker_option.is_selected()
        @select_element.val("")
      else
        @select_element.val(selected_value)
    unless both_array_are_equal(old_values, @selected_values())
      @select_element.change()
      @options.changed.call(@select_element, old_values, @selected_values(), original_event) if @options.changed?

  clear_selected: () ->
    piker = this
    (e)->
      piker.select_element.val("").trigger('change')


class Bootstrap4ImagePickerOption
  constructor: (option_element, @picker, @options = {}) ->
    @option_element = jQuery(option_element)
    @create_node()

  do_search: (filter) ->
    if @option_element.data("img-label")
      text = @option_element.data("img-label")

    text += ' ' + @option_element.text()

    text.toLowerCase().indexOf(filter) > -1

  destroy: ->
    @node.find(".grid-item").off("click", @click_handler)

  has_image: () ->
    @option_element.data("img-src")?

  is_blank: () ->
    !(@value()? && @value() != "")

  is_selected: () ->
    select_value = @picker.select_element.val()
    if @picker.multiple
      jQuery.inArray(@value(), select_value) >= 0
    else
      @value() == select_value

  mark_as_selected: () ->
    if !@check
      @check = jQuery(@options.template.check)
      @node.find(".card").addClass("selected").append(@check)

  unmark_as_selected: () ->
    if @check
      @check.remove()
      @check = null
    @node.find(".card").removeClass("selected")

  value: () ->
    @option_element.val()

  label: () ->
    if @option_element.data("img-label")
      @option_element.data("img-label")
    else
      @option_element.text()

  click_handler: (event) =>
    @picker.toggle(this, event)
    @options.clicked.call(@picker.select_element, this, event)  if @options.clicked?
    @options.selected.call(@picker.select_element, this, event) if @options.selected? and @is_selected()

  create_node: () ->
    @node = jQuery(@options.template.item)

    image = jQuery(@options.template.image)
    image.attr("src", @option_element.data("img-src"))

    label = jQuery(@options.template.label)

    # Add custom class
    imgClass = @option_element.data("img-class")
    if imgClass
      @node.addClass(imgClass)
      image.addClass(imgClass)


    # Add image alt
    imgAlt = @option_element.data("img-alt")
    if imgAlt
      image.attr('alt', imgAlt);

    # label contents
    label.find('content').replaceWith(@label())

    # set click handler
    @node.on("click", @click_handler)

    # add image
    @node.find('content').replaceWith(if @options.show_label then image.add(label) else image)

    @node


class Bootstrap4ImagePickerDetailPanel
  constructor: (@picker_obj, @options = {}, @element = {}) ->
#		@element = jQuery(@options.template.details)
    @selected = jQuery(@options.template.detail_label)
    @selected.on('click', @picker_obj.clear_selected())
    @selected.tooltip(@options.tooltip_options)
    @element.append(@selected)

    @filtered = jQuery(@options.template.filter_label)
    @element.append(@filtered)

    @filter_clear = jQuery(@options.template.filter_clear)
    @filter_clear.on('click', @picker_obj.search.clear_search())
    @element.append(@filter_clear)

    @show_selected = jQuery(@options.template.filter_selected_only)
    @show_selected.on('click', @picker_obj.search.show_selected(@picker_obj))
    @element.append(@show_selected)

    @show_unselected = jQuery(@options.template.filter_unselected_only)
    @show_unselected.on('click', @picker_obj.search.show_unselected(@picker_obj))
    @element.append(@show_unselected)

    @update_details()

    @element

  update_details: () ->
    @selected_details()
    @filtered_details()

  selected_details: () ->
    total = @picker_obj.picker_options.length
    select = @picker_obj.selected_values().length

    @selected.find('.badge.badge-info').html("#{select} of #{total}")

    if select
      @selected.removeClass('cursor-default').addClass('cursor-clickable')
    else
      @selected.removeClass('cursor-clickable').addClass('cursor-default')

  filtered_details: () ->
    total = @picker_obj.picker_options.length
    filtered_count = @picker_obj.search.filtered_count

    @filtered.find('.badge.badge-warning').html("#{total - filtered_count} of #{total}")

    if filtered_count
      @filtered.removeClass('cursor-default').addClass('cursor-clickable')
    else
      @filtered.removeClass('cursor-clickable').addClass('cursor-default')


class Bootstrap4ImagePickerSearchBar
  constructor: (@picker_obj, @options = {}) ->
    @filtered_count = 0

    @element = jQuery(@options.template.search)

    @element.find('input').on("change paste keyup", @search_handler(@picker_obj, @options))

    @element

  show_selected: (picker) ->
    searchbar = this
    (e)->
      searchbar.filtered_count = 0

      jQuery.grep(picker.picker_options, ((element, index)->
        r = element.is_selected()
        searchbar.filtered_count += 1 unless r
        element.node.toggle(r)
      ))

      picker.details.update_details()

  show_unselected: (picker) ->
    searchbar = this
    (e)->
      searchbar.filtered_count = 0

      jQuery.grep(picker.picker_options, ((element, index)->
        r = element.is_selected()
        searchbar.filtered_count += 1 if r
        element.node.toggle(!r)
      ))

      picker.details.update_details()


  clear_search: () ->
    searchbar = this
    (e)->
      searchbar.element.find('input').val("").trigger('change')

  search_handler: (picker, options) ->
    searchbar = this
    (e)->
      searchbar.filtered_count = 0

      if !options.search_handler
        q = jQuery(this).val()
        jQuery.grep(picker.picker_options, ((element, index)->
          r = element.do_search(q)
          searchbar.filtered_count += 1 unless r
          element.node.toggle(r)))
      else
        options.search_handler()

      picker.details.update_details()
