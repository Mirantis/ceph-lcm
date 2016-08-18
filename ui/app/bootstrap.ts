import { Component, Input } from '@angular/core';

@Component({
  selector: 'modal',
  template: `
<div class="modal fade" [id]="id" tabindex="-1" role="dialog" aria-hidden="true">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        <ng-content select=".modal-title"></ng-content>
      </div>
      <ng-content select=".modal-body"></ng-content>
      <ng-content select=".modal-footer"></ng-content>
    </div>
  </div>
</div>
`
})
export class Modal {
  @Input() id: string = 'modal';

  show(id: string = 'modal') {
    $('#' + id).modal('show');
  }

  close(id: string = 'modal') {
    $('#' + id).modal('hide');
  }
}