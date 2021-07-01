from bokeh.core.properties import Image, Bool, String, Nullable
from bokeh.models import Tool
from bokeh.util.compiler import TypeScript

TS_CODE = """
import {InspectTool, InspectToolView} from
                    "models/tools/inspectors/inspect_tool"
import * as p from "core/properties"

export class CustomInspectToolView extends InspectToolView {
  model: CustomInspectTool
  connect_signals(): void {
      super.connect_signals()

      this.connect(this.model.properties.active.change, () => {
          this.model._active = this.model.active
      })
  }
}

export namespace CustomInspectTool {
  export type Attrs = p.AttrsOf<Props>

  export type Props = InspectTool.Props & {
    _active: p.Property<Boolean>
    icon: p.Property<string>
    tool_name: p.Property<string>
  }
}

export interface CustomInspectTool extends CustomInspectTool.Attrs {}

export class CustomInspectTool extends InspectTool {
  properties: CustomInspectTool.Props
  __view_type__: CustomInspectToolView

  constructor(attrs?: Partial<CustomInspectTool.Attrs>) {
    super(attrs)
  }

  static init_CustomInspectTool(): void {
    this.prototype.default_view = CustomInspectToolView

    this.define<CustomInspectTool.Props>({
      _active:   [ p.Instance ],
      icon:      [ p.String   ],
      tool_name: [p.String   ]
    })
  }
}
"""


class CustomInspectTool(Tool):
    __implementation__ = TypeScript(TS_CODE)
    _active = Nullable(Bool)
    icon = Image()
    tool_name = String()
