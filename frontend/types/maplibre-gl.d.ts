declare module 'maplibre-gl' {
  export class LngLat {
    constructor(lng: number, lat: number)
    lng: number
    lat: number
  }

  export class LngLatBounds {
    constructor(sw?: LngLat, ne?: LngLat)
    extend(obj: LngLat | LngLatBounds | [number, number]): this
    getCenter(): LngLat
    getSouthWest(): LngLat
    getNorthEast(): LngLat
  }

  export class Marker {
    constructor(options?: { element?: HTMLElement; anchor?: string; offset?: [number, number] })
    setLngLat(lnglat: LngLat | [number, number]): this
    setPopup(popup: Popup): this
    addTo(map: Map): this
    remove(): this
  }

  export class Popup {
    constructor(options?: { offset?: number | [number, number]; maxWidth?: string; closeButton?: boolean })
    setHTML(html: string): this
    setText(text: string): this
    addTo(map: Map): this
    remove(): this
  }

  export class Map {
    constructor(options: {
      container: HTMLElement | string
      style?: any
      center?: [number, number] | LngLat
      zoom?: number
      maxZoom?: number
      minZoom?: number
      pitch?: number
      bearing?: number
    })
    addControl(control: Control, position?: string): this
    removeControl(control: Control): this
    addSource(id: string, source: any): this
    removeSource(id: string): this
    addLayer(layer: any, beforeId?: string): this
    removeLayer(id: string): this
    getLayer(id: string): any
    getSource(id: string): any
    on(type: string, listener: Function): this
    off(type: string, listener?: Function): this
    fitBounds(bounds: LngLatBounds, options?: any): this
    flyTo(options: any): this
    setCenter(center: [number, number] | LngLat): this
    setZoom(zoom: number): this
    getCenter(): LngLat
    getZoom(): number
    remove(): this
  }

  export class NavigationControl {
    constructor(options?: { showCompass?: boolean; showZoom?: boolean; visualizePitch?: boolean })
  }

  export class ScaleControl {
    constructor(options?: { maxWidth?: number; unit?: string })
  }

  export class GeolocateControl {
    constructor(options?: any)
  }

  type Control = NavigationControl | ScaleControl | GeolocateControl
}

declare module 'maplibre-gl/dist/maplibre-gl.css' {
  const content: string
  export default content
}
