# SPDX-FileCopyrightText: Copyright (c) 2020-2025, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from bokeh.core.properties import Bool, Nullable
from bokeh.models import Tool
from bokeh.util.compiler import TypeScript

TS_CODE = """
import {InspectTool, InspectToolView} from
                    "models/tools/inspectors/inspect_tool"
import * as p from "core/properties"

export class CustomInspectToolView extends InspectToolView {
  declare model: CustomInspectTool
  connect_signals(): void {
      super.connect_signals()

      this.on_change([this.model.properties.active], () => {
        this.model._active = this.model.active
      })
  }
}

export namespace CustomInspectTool {
  export type Attrs = p.AttrsOf<Props>

  export type Props = InspectTool.Props & {
    _active: p.Property<boolean>
  }
}

export interface CustomInspectTool extends CustomInspectTool.Attrs {}

export class CustomInspectTool extends InspectTool {
  declare properties: CustomInspectTool.Props
  declare __view_type__: CustomInspectToolView

  constructor(attrs?: Partial<CustomInspectTool.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = CustomInspectToolView

    this.define<CustomInspectTool.Props>(({Boolean}) => ({
      _active: [ Boolean, true ]
    }))

    this.register_alias("customInspect", () => new CustomInspectTool())
  }

}
"""


class CustomInspectTool(Tool):
    __implementation__ = TypeScript(TS_CODE)
    _active = Nullable(Bool)
