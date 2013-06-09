Bambu is a set of tools for building websites and apps in Django.

## Activity stream

When you create a model in Django, you can register it with ``bambu.activity`` to create a stream that updates whenever the model's objects are created, updated or deleted. Create multiple streams for different sections of a site, and display them with a simple template tag.

## API

Quickly expose your models to a JSON or XML API, authenticated via HTTP or OAuth. Create API classes like you do with ``django.contrib.admin`` and add documentation that ``bambu.api`` automatically displays to developers.

## Bootstrap

Use Twitter's [Bootstrap](http://twitter.github.com/bootstrap/) CSS framework to build your app. All the views Bambu uses all extend a base template which you create, that can be based on a skeleton Bootstrap template. Shortcut tags let you easily add breadcrumb trails and icons to your apps.

## Cron

A simple scheduling system that lets you define jobs that get performed at various intervals. Use a virtual "poor man's cron" or a single Django management command to run the jobs.

## Megaphone

Automatically post to Twitter, Facebook, LinkedIn and Buffer (with the option of creating your own providers) whenever certain custom-defined actions happen, like publishing a blog post or uploading a video. Register a model with ``bambu.megaphone`` and the app will automatically post your content to that serveice. You can connect your profiles up using the admin area, or let non-staff users set it up for themselves via their profile.

## SaaS and Payments

Use this burgeoning toolset to build a SaaS (Software as a Service) package, which can take recurring payments (currently from PayPal).

## Blog, comments, enquiries, FAQ and pages

Run a standard website with a number of pages, a simple blog (with comments), a Frequently Asked Questions section and an enquiries form, using Bambu Tools. Add the apps to your ``INSTALLED_APPS`` settings, hook up the URL patterns then sync your database. That's it!

## Other tools

Bambu can store attachments next to any model and display links or thumbnails within the body of your text via a simple template filter. It also includes ``bambu.navigation`` which builds dynamic, customisable menus for your site, which any reusable app can hook into. ``bambu.oembed`` provides a template filter that turns web addresses into embeddable content.

Still further tools include wrappers for Uploadify, JWPlayer, Google Analytics and Cookie Control, a preview system which other apps can utilise, a Python interface for ffmpeg, a simple templated email system which supports HTML and text-only emails without the need for separate templates, Open Graph support and the running of asynchronous tasks.

All in all, Bambu Tools is a beast.