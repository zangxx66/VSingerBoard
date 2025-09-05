import NProgress from 'nprogress' 

NProgress.configure({
    easing: "ease",
    speed: 500,
    showSpinner: false,
    trickleSpeed: 200,
    minimum: 0.3,
    parent: "body"
})

export const start = () => {
    NProgress.start()
}

export const stop = () => {
    NProgress.done()
}
